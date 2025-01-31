# -*- coding: utf-8 -*-

import datetime
from lxml import etree
from dateutil.relativedelta import relativedelta
import re
import logging
from pytz import timezone

import requests

from odoo import api, fields, models
from odoo.addons.web.controllers.main import xml2json_from_elementtree
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

BANXICO_DATE_FORMAT = '%d/%m/%Y'
CBUAE_URL = "https://www.centralbank.ae/en/fx-rates"
CBUAE_CURRENCIES = {
    'US Dollar': 'USD',
    'Argentine Peso': 'ARS',
    'Australian Dollar': 'AUD',
    'Bangladesh Taka': 'BDT',
    'Bahrani Dinar': 'BHD',
    'Brunei Dollar': 'BND',
    'Brazilian Real': 'BRL',
    'Botswana Pula': 'BWP',
    'Belarus Rouble': 'BYN',
    'Canadian Dollar': 'CAD',
    'Swiss Franc': 'CHF',
    'Chilean Peso': 'CLP',
    'Chinese Yuan - Offshore': 'CNY',
    'Chinese Yuan': 'CNY',
    'Colombian Peso': 'COP',
    'Czech Koruna': 'CZK',
    'Danish Krone': 'DKK',
    'Algerian Dinar': 'DZD',
    'Egypt Pound': 'EGP',
    'Euro': 'EUR',
    'GB Pound': 'GBP',
    'Hongkong Dollar': 'HKD',
    'Hungarian Forint': 'HUF',
    'Indonesia Rupiah': 'IDR',
    'Indian Rupee': 'INR',
    'Iceland Krona': 'ISK',
    'Jordan Dinar': 'JOD',
    'Japanese Yen': 'JPY',
    'Kenya Shilling': 'KES',
    'Korean Won': 'KRW',
    'Kuwaiti Dinar': 'KWD',
    'Kazakhstan Tenge': 'KZT',
    'Lebanon Pound': 'LBP',
    'Sri Lanka Rupee': 'LKR',
    'Moroccan Dirham': 'MAD',
    'Macedonia Denar': 'MKD',
    'Mexican Peso': 'MXN',
    'Malaysia Ringgit': 'MYR',
    'Nigerian Naira': 'NGN',
    'Norwegian Krone': 'NOK',
    'NewZealand Dollar': 'NZD',
    'Omani Rial': 'OMR',
    'Peru Sol': 'PEN',
    'Philippine Piso': 'PHP',
    'Pakistan Rupee': 'PKR',
    'Polish Zloty': 'PLN',
    'Qatari Riyal': 'QAR',
    'Serbian Dinar': 'RSD',
    'Russia Rouble': 'RUB',
    'Saudi Riyal': 'SAR',
    'Swedish Krona': 'SWK',
    'Singapore Dollar': 'SGD',
    'Thai Baht': 'THB',
    'Tunisian Dinar': 'TND',
    'Turkish Lira': 'TRY',
    'Trin Tob Dollar': 'TTD',
    'Taiwan Dollar': 'TWD',
    'Tanzania Shilling': 'TZS',
    'Uganda Shilling': 'UGX',
    'Vietnam Dong': 'VND',
    'South Africa Rand': 'ZAR',
    'Zambian Kwacha': 'ZMW',
}

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_interval_unit = fields.Selection([
        ('manually', 'Manually'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')],
        default='manually', string='Interval Unit')
    currency_next_execution_date = fields.Date(string="Next Execution Date")
    currency_provider = fields.Selection([
        ('ecb', 'European Central Bank'),
        ('fta', 'Federal Tax Administration (Switzerland)'),
        ('banxico', 'Mexican Bank'),
        ('boc', 'Bank Of Canada'),
        ('xe_com', 'xe.com'),
        ('bnr', 'National Bank Of Romania'),
        ('mindicador', 'Chilean mindicador.cl'),
        ('bcrp', 'Bank of Peru'),
        ('cbuae', 'UAE Central Bank'),
    ], default='ecb', string='Service Provider')

    @api.model
    def create(self, vals):
        ''' Change the default provider depending on the company data.'''
        if vals.get('country_id') and 'currency_provider' not in vals:
            code_providers = {'CH' : 'fta', 'MX': 'banxico', 'CA' : 'boc', 'RO': 'bnr', 'CL': 'mindicador', 'PE': 'bcrp', 'AE': 'cbuae'}
            cc = self.env['res.country'].browse(vals['country_id']).code.upper()
            if cc in code_providers:
                vals['currency_provider'] = code_providers[cc]
        return super(ResCompany, self).create(vals)

    @api.model
    def set_special_defaults_on_install(self):
        ''' At module installation, set the default provider depending on the company country.'''
        all_companies = self.env['res.company'].search([])
        currency_providers = {
            'CH': 'fta',  # Sets FTA as the default provider for every swiss company that was already installed
            'MX': 'banxico',  # Sets Banxico as the default provider for every mexican company already installed
            'CA': 'boc',  # Bank of Canada
            'RO': 'bnr',
            'CL': 'mindicador',
            'PE': 'bcrp',
            'AE': 'cbuae',
        }
        for company in all_companies:
            company.currency_provider = currency_providers.get(company.country_id.code, 'ecb')

    def update_currency_rates(self):
        ''' This method is used to update all currencies given by the provider.
        It calls the parse_function of the selected exchange rates provider automatically.

        For this, all those functions must be called _parse_xxx_data, where xxx
        is the technical name of the provider in the selection field. Each of them
        must also be such as:
            - It takes as its only parameter the recordset of the currencies
              we want to get the rates of
            - It returns a dictionary containing currency codes as keys, and
              the corresponding exchange rates as its values. These rates must all
              be based on the same currency, whatever it is. This dictionary must
              also include a rate for the base currencies of the companies we are
              updating rates from, otherwise this will result in an error
              asking the user to choose another provider.

        :return: True if the rates of all the records in self were updated
                 successfully, False if at least one wasn't.
        '''
        rslt = True
        active_currencies = self.env['res.currency'].search([])
        for (currency_provider, companies) in self._group_by_provider().items():
            parse_results = None
            parse_function = getattr(companies, '_parse_' + currency_provider + '_data')
            parse_results = parse_function(active_currencies)

            if parse_results == False:
                # We check == False, and don't use bool conversion, as an empty
                # dict can be returned, if none of the available currencies is supported by the provider
                _logger.warning('Unable to connect to the online exchange rate platform %s. The web service may be temporary down.', currency_provider)
                rslt = False
            else:
                companies._generate_currency_rates(parse_results)

        return rslt

    def _group_by_provider(self):
        """ Returns a dictionnary grouping the companies in self by currency
        rate provider. Companies with no provider defined will be ignored."""
        rslt = {}
        for company in self:
            if not company.currency_provider:
                continue

            if rslt.get(company.currency_provider):
                rslt[company.currency_provider] += company
            else:
                rslt[company.currency_provider] = company
        return rslt

    def _generate_currency_rates(self, parsed_data):
        """ Generate the currency rate entries for each of the companies, using the
        result of a parsing function, given as parameter, to get the rates data.

        This function ensures the currency rates of each company are computed,
        based on parsed_data, so that the currency of this company receives rate=1.
        This is done so because a lot of users find it convenient to have the
        exchange rate of their main currency equal to one in Odoo.
        """
        Currency = self.env['res.currency']
        CurrencyRate = self.env['res.currency.rate']

        today = fields.Date.today()
        for company in self:
            rate_info = parsed_data.get(company.currency_id.name, None)

            if not rate_info:
                raise UserError(_("Your main currency (%s) is not supported by this exchange rate provider. Please choose another one.", company.currency_id.name))

            base_currency_rate = rate_info[0]

            for currency, (rate, date_rate) in parsed_data.items():
                rate_value = rate/base_currency_rate

                currency_object = Currency.search([('name','=',currency)])
                already_existing_rate = CurrencyRate.search([('currency_id', '=', currency_object.id), ('name', '=', date_rate), ('company_id', '=', company.id)])
                if already_existing_rate:
                    already_existing_rate.rate = rate_value
                else:
                    CurrencyRate.create({'currency_id': currency_object.id, 'rate': rate_value, 'name': date_rate, 'company_id': company.id})

    def _parse_fta_data(self, available_currencies):
        ''' Parses the data returned in xml by FTA servers and returns it in a more
        Python-usable form.'''
        request_url = 'https://www.backend-rates.ezv.admin.ch/api/xmldaily?d=today&locale=en'
        try:
            parse_url = requests.request('GET', request_url)
        except:
            return False

        rates_dict = {}
        available_currency_names = available_currencies.mapped('name')
        xml_tree = etree.fromstring(parse_url.content)
        data = xml2json_from_elementtree(xml_tree)
        for child_node in data['children']:
            if child_node['tag'] == 'devise':
                currency_code = child_node['attrs']['code'].upper()

                if currency_code in available_currency_names:
                    currency_xml = None
                    rate_xml = None

                    for sub_child in child_node['children']:
                        if sub_child['tag'] == 'waehrung':
                            currency_xml = sub_child['children'][0]
                        elif sub_child['tag'] == 'kurs':
                            rate_xml = sub_child['children'][0]
                        if currency_xml and rate_xml:
                            #avoid iterating for nothing on children
                            break

                    rates_dict[currency_code] = (float(re.search('\d+',currency_xml).group()) / float(rate_xml), fields.Date.today())

        if 'CHF' in available_currency_names:
            rates_dict['CHF'] = (1.0, fields.Date.today())

        return rates_dict

    def _parse_ecb_data(self, available_currencies):
        ''' This method is used to update the currencies by using ECB service provider.
            Rates are given against EURO
        '''
        request_url = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        try:
            parse_url = requests.request('GET', request_url)
        except:
            #connection error, the request wasn't successful
            return False

        xmlstr = etree.fromstring(parse_url.content)
        data = xml2json_from_elementtree(xmlstr)
        node = data['children'][2]['children'][0]
        available_currency_names = available_currencies.mapped('name')
        rslt = {x['attrs']['currency']:(float(x['attrs']['rate']), fields.Date.today()) for x in node['children'] if x['attrs']['currency'] in available_currency_names}

        if rslt and 'EUR' in available_currency_names:
            rslt['EUR'] = (1.0, fields.Date.today())

        return rslt

    def _parse_cbuae_data(self, available_currencies):
        ''' This method is used to update the currencies by using UAE Central Bank service provider.
            Exchange rates are expressed as 1 unit of the foreign currency converted into AED
        '''
        try:
            fetched_data = requests.get(CBUAE_URL, timeout=30)
            fetched_data.raise_for_status()
        except Exception:
            return False

        htmlelem = etree.fromstring(fetched_data.content, etree.HTMLParser())
        rates_entries = htmlelem.xpath("//table[@id='ratesDateTable']/tbody/tr")
        available_currency_names = set(available_currencies.mapped('name'))
        rslt = {}
        for rate_entry in rates_entries:
            # line structure is <td>Currency Description</td><td>rate</td>
            currency_code = CBUAE_CURRENCIES.get(rate_entry[0].text)
            rate = float(rate_entry[1].text)
            if currency_code in available_currency_names:
                rslt[currency_code] = (1.0/rate, fields.Date.today())

        if 'AED' in available_currency_names:
            rslt['AED'] = (1.0, fields.Date.today())
        return rslt

    def _parse_boc_data(self, available_currencies):
        """This method is used to update currencies exchange rate by using Bank
           Of Canada daily exchange rate service.
           Exchange rates are expressed as 1 unit of the foreign currency converted into Canadian dollars.
           Keys are in this format: 'FX{CODE}CAD' e.g.: 'FXEURCAD'
        """
        available_currency_names = available_currencies.mapped('name')

        request_url = "http://www.bankofcanada.ca/valet/observations/group/FX_RATES_DAILY/json"
        try:
            response = requests.request('GET', request_url)
        except:
            #connection error, the request wasn't successful
            return False
        if not 'application/json' in response.headers.get('Content-Type', ''):
            return False
        data = response.json()

        # 'observations' key contains rates observations by date
        last_observation_date = sorted([obs['d'] for obs in data['observations']])[-1]
        last_obs = [obs for obs in data['observations'] if obs['d'] == last_observation_date][0]
        last_obs.update({'FXCADCAD': {'v': '1'}})
        rslt = {}
        if 'CAD' in available_currency_names:
            rslt['CAD'] = (1, fields.Date.today())

        for currency_name in available_currency_names:
            currency_obs = last_obs.get('FX{}CAD'.format(currency_name), None)
            if currency_obs is not None:
                rslt[currency_name] = (1.0/float(currency_obs['v']), fields.Date.today())

        return rslt

    def _parse_banxico_data(self, available_currencies):
        """Parse function for Banxico provider.
        * With basement in legal topics in Mexico the rate must be **one** per day and it is equal to the rate known the
        day immediate before the rate is gotten, it means the rate for 02/Feb is the one at 31/jan.
        * The base currency is always MXN but with the inverse 1/rate.
        * The official institution is Banxico.
        * The webservice returns the following currency rates:
            - SF46410 EUR
            - SF60632 CAD
            - SF43718 USD Fixed
            - SF46407 GBP
            - SF46406 JPY
            - SF60653 USD SAT - Officially used from SAT institution
        Source: http://www.banxico.org.mx/portal-mercado-cambiario/
        """
        icp = self.env['ir.config_parameter'].sudo()
        token = icp.get_param('banxico_token')
        if not token:
            # https://www.banxico.org.mx/SieAPIRest/service/v1/token
            token = 'd03cdee20272f1edc5009a79375f1d942d94acac8348a33245c866831019fef4'  # noqa
            icp.set_param('banxico_token', token)
        foreigns = {
            # position order of the rates from webservices
            'SF46410': 'EUR',
            'SF60632': 'CAD',
            'SF46406': 'JPY',
            'SF46407': 'GBP',
            'SF60653': 'USD',
        }
        url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/%s/datos/%s/%s?token=%s' # noqa
        try:
            date_mx = datetime.datetime.now(timezone('America/Mexico_City'))
            today = date_mx.strftime(DEFAULT_SERVER_DATE_FORMAT)
            yesterday = (date_mx - datetime.timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            res = requests.get(url % (','.join(foreigns), yesterday, today, token))
            res.raise_for_status()
            series = res.json()['bmx']['series']
            series = {serie['idSerie']: {dato['fecha']: dato['dato'] for dato in serie['datos']} for serie in series if 'datos' in serie}
        except:
            return False

        available_currency_names = available_currencies.mapped('name')

        rslt = {
            'MXN': (1.0, fields.Date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)),
        }

        today = date_mx.strftime(BANXICO_DATE_FORMAT)
        yesterday = (date_mx - datetime.timedelta(days=1)).strftime(BANXICO_DATE_FORMAT)
        for index, currency in foreigns.items():
            if not series.get(index, False):
                continue
            if currency not in available_currency_names:
                continue

            serie = series[index]
            for rate in serie:
                try:
                    foreign_mxn_rate = float(serie[rate])
                except (ValueError, TypeError):
                    continue
                foreign_rate_date = datetime.datetime.strptime(rate, BANXICO_DATE_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
                rslt[currency] = (1.0/foreign_mxn_rate, foreign_rate_date)
        return rslt

    def _parse_xe_com_data(self, available_currencies):
        """ Parses the currency rates data from xe.com provider.
        As this provider does not have an API, we directly extract what we need
        from HTML.
        """
        url_format = 'http://www.xe.com/currencytables/?from=%(currency_code)s'
        today = fields.Date.today()

        # We generate all the exchange rates relative to the USD. This is purely arbitrary.
        try:
            fetched_data = requests.request('GET', url_format % {'currency_code': 'USD'})
        except:
            return False

        rslt = {}

        available_currency_names = available_currencies.mapped('name')

        if 'USD' in available_currency_names:
            rslt['USD'] = (1.0, today)

        htmlelem = etree.fromstring(fetched_data.content, etree.HTMLParser())
        rates_entries = htmlelem.xpath(".//div[@id='table-section']//tbody/tr")
        for rate_entry in rates_entries:
            # line structure is <th>CODE</th><td>NAME<td><td>UNITS PER CURRENCY</td><td>CURRENCY PER UNIT</td>
            currency_code = ''.join(rate_entry.find('.//th').itertext()).strip()
            if currency_code in available_currency_names:
                rate = float(rate_entry.find("td[2]").text.replace(',', ''))
                rslt[currency_code] = (rate, today)

        return rslt

    def _parse_bnr_data(self, available_currencies):
        ''' This method is used to update the currencies by using
        BNR service provider. Rates are given against RON
        '''
        request_url = "https://www.bnr.ro/nbrfxrates.xml"
        try:
            parse_url = requests.request('GET', request_url)
        except:
            #connection error, the request wasn't successful
            return False

        xmlstr = etree.fromstring(parse_url.content)
        data = xml2json_from_elementtree(xmlstr)
        available_currency_names = available_currencies.mapped('name')
        rate_date = fields.Date.today()
        rslt = {}
        rates_node = data['children'][1]['children'][2]
        if rates_node:
            rate_date = (datetime.datetime.strptime(
                rates_node['attrs']['date'], DEFAULT_SERVER_DATE_FORMAT
            ) + datetime.timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            for x in rates_node['children']:
                if x['attrs']['currency'] in available_currency_names:
                    rslt[x['attrs']['currency']] = (
                        float(x['attrs'].get('multiplier', '1')) / float(x['children'][0]),
                        rate_date
                    )
        if rslt and 'RON' in available_currency_names:
            rslt['RON'] = (1.0, rate_date)
        return rslt

    def _parse_bcrp_data(self, available_currencies):
        """Bank of Peru (bcrp)
        API Doc: https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api
            - https://estadisticas.bcrp.gob.pe/estadisticas/series/api/[códigos de series]/[formato de salida]/[periodo inicial]/[periodo final]/[idioma]
        Source: https://estadisticas.bcrp.gob.pe/estadisticas/series/diarias/tipo-de-cambio
            PD04640PD	TC Sistema bancario SBS (S/ por US$) - Venta
            PD04648PD	TC Euro (S/ por Euro) - Venta
        """

        bcrp_date_format_url = '%Y-%m-%d'
        bcrp_date_format_res = '%d.%b.%y'
        result = {}
        available_currency_names = available_currencies.mapped('name')
        if 'PEN' not in available_currency_names:
            return result
        result['PEN'] = (1.0, fields.Date.context_today(self.with_context(tz='America/Lima')))
        url_format = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/%(currency_code)s/json/%(date_start)s/%(date_end)s/ing"
        foreigns = {
            # currency code from webservices
            'USD': 'PD04640PD',
            'EUR': 'PD04648PD',
        }
        date_pe = self.mapped('currency_next_execution_date')[0] or datetime.datetime.now(timezone('America/Lima'))
        # In case the desired date does not have an exchange rate, it means that we must use the previous day until we
        # find a change. It is left 7 since in tests we have found cases of up to 5 days without update but no more
        # than that. That is not to say that that cannot change in the future, so we leave a little margin.
        first_pe_str = (date_pe - datetime.timedelta(days=7)).strftime(bcrp_date_format_url)
        second_pe_str = date_pe.strftime(bcrp_date_format_url)
        data = {
            'date_start': first_pe_str,
            'date_end': second_pe_str,
        }
        for currency_odoo_code, currency_pe_code in foreigns.items():
            if currency_odoo_code not in available_currency_names:
                continue
            data.update({'currency_code': currency_pe_code})
            url = url_format % data
            try:
                res = requests.get(url, timeout=10)
                res.raise_for_status()
                series = res.json()
            except Exception as e:
                _logger.error(e)
                continue
            date_rate_str = series['periods'][-1]['name']
            fetched_rate = float(series['periods'][-1]['values'][0])
            rate = 1.0 / fetched_rate if fetched_rate else 0
            if not rate:
                continue
            # This replace is done because the service is returning Set for September instead of Sep the value
            # commonly accepted for September,
            normalized_date = date_rate_str.replace('Set', 'Sep')
            date_rate = datetime.datetime.strptime(normalized_date, bcrp_date_format_res).strftime(DEFAULT_SERVER_DATE_FORMAT)
            result[currency_odoo_code] = (rate, date_rate)
        return result

    def _parse_mindicador_data(self, available_currencies):
        """Parse function for mindicador.cl provider for Chile
        * Regarding needs of rates in Chile there will be one rate per day, except for UTM index (one per month)
        * The value of the rate is the "official" rate
        * The base currency is always CLP but with the inverse 1/rate.
        * The webservice returns the following currency rates:
            - EUR
            - USD (Dolar Observado)
            - UF (Unidad de Fomento)
            - UTM (Unidad Tributaria Mensual)
        """
        icp = self.env['ir.config_parameter'].sudo()
        server_url = icp.get_param('mindicador_api_url', False)
        if not server_url:
            server_url = 'https://mindicador.cl/api'
            icp.set_param('mindicador_api_url', server_url)
        foreigns = {
            "USD": ["dolar", "Dolares"],
            "EUR": ["euro", "Euros"],
            "UF": ["uf", "UFs"],
            "UTM": ["utm", "UTMs"],
        }
        available_currency_names = available_currencies.mapped('name')
        _logger.debug('mindicador: available currency names: %s' % available_currency_names)
        today_date = fields.Date.context_today(self.with_context(tz='America/Santiago'))
        rslt = {
            'CLP': (1.0, today_date.strftime(DEFAULT_SERVER_DATE_FORMAT)),
        }
        request_date = today_date.strftime('%d-%m-%Y')
        for index, currency in foreigns.items():
            if index not in available_currency_names:
                _logger.debug('Index %s not in available currency name' % index)
                continue
            url = server_url + '/%s/%s' % (currency[0], request_date)
            try:
                res = requests.get(url)
                res.raise_for_status()
            except Exception as e:
                return False
            if 'html' in res.text:
                return False
            data_json = res.json()
            if len(data_json['serie']) == 0:
                continue
            date = data_json['serie'][0]['fecha'][:10]
            rate = data_json['serie'][0]['valor']
            rslt[index] = (1.0 / rate,  date)
        return rslt

    @api.model
    def run_update_currency(self):
        """ This method is called from a cron job to update currency rates.
        """
        records = self.search([('currency_next_execution_date', '<=', fields.Date.today())])
        if records:
            to_update = self.env['res.company']
            for record in records:
                if record.currency_interval_unit == 'daily':
                    next_update = relativedelta(days=+1)
                elif record.currency_interval_unit == 'weekly':
                    next_update = relativedelta(weeks=+1)
                elif record.currency_interval_unit == 'monthly':
                    next_update = relativedelta(months=+1)
                else:
                    record.currency_next_execution_date = False
                    continue
                record.currency_next_execution_date = datetime.date.today() + next_update
                to_update += record
            to_update.update_currency_rates()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_interval_unit = fields.Selection(related="company_id.currency_interval_unit", readonly=False)
    currency_provider = fields.Selection(related="company_id.currency_provider", readonly=False)
    currency_next_execution_date = fields.Date(related="company_id.currency_next_execution_date", readonly=False)

    @api.onchange('currency_interval_unit')
    def onchange_currency_interval_unit(self):
        #as the onchange is called upon each opening of the settings, we avoid overwriting
        #the next execution date if it has been already set
        if self.company_id.currency_next_execution_date:
            return
        if self.currency_interval_unit == 'daily':
            next_update = relativedelta(days=+1)
        elif self.currency_interval_unit == 'weekly':
            next_update = relativedelta(weeks=+1)
        elif self.currency_interval_unit == 'monthly':
            next_update = relativedelta(months=+1)
        else:
            self.currency_next_execution_date = False
            return
        self.currency_next_execution_date = datetime.date.today() + next_update

    def update_currency_rates_manually(self):
        self.ensure_one()

        if not (self.company_id.update_currency_rates()):
            raise UserError(_('Unable to connect to the online exchange rate platform. The web service may be temporary down. Please try again in a moment.'))
