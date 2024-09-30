from odoo import fields, models, api, _
import requests
from odoo.exceptions import UserError


class TrackAndTrace(models.Model):
    _name = 'track.and.trace'
    _rec_name = 'bar_code'
    _description = 'Gets Tracking Information About The Shipment'

    # Shipment Master Data Fields
    carrier_id = fields.Many2one(comodel_name='track.and.trace.carriers', string='Carrier', required=True)
    country_code = fields.Char(string='Country Code', required=True)
    bar_code = fields.Char(string='Bar code', help="The bar code of the shipment", required=True)

    # ---------> Shipment Info Fields
    carrier = fields.Many2one(comodel_name='track.and.trace.carriers', string='Carrier', readonly=True)
    carrier_weight = fields.Float('Carrier Weight', readonly=True)
    customer_reference = fields.Char('Customer Reference', readonly=True)
    delivery_date = fields.Char('Delivery Date', readonly=True)
    information_source = fields.Char('Information Source', readonly=True)
    lang_code = fields.Char('Lang Code', readonly=True)
    order_number = fields.Char('Order Number', readonly=True)
    original_carrier = fields.Char('Original Carrier', readonly=True)
    package_number = fields.Char('Package Number', readonly=True)
    pickUp_date = fields.Char('Pick UpDate', readonly=True)
    product = fields.Char('Product', readonly=True)
    weight = fields.Char('Weight', readonly=True)

    # --------> Receiver Info Fields
    address = fields.Char('Address', readonly=True)
    business_name = fields.Char('Business Name', readonly=True)
    city = fields.Char('City', readonly=True)
    contact_name = fields.Char('Contact Name', readonly=True)
    country = fields.Char('Country', readonly=True)
    zip = fields.Char('Zip', readonly=True)

    # ----------> Scan Info
    scan_ids = fields.One2many(comodel_name='track.and.trace.scan.line', inverse_name='track_and_trace_id',
                               string='Scans', required=False)

    # ----------> Sender Info Fields
    senders_reference = fields.Char('SendersReference', readonly=True)
    signature_image = fields.Char('Signature Image', readonly=True)
    signature_name = fields.Char('Signature Name', readonly=True)

    # To Show  Notification
    def show_notification(self, title, message, type):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _(title),
                'message': _(message),
                'type': type,  # types: success,warning,danger,info
                'sticky': False,  # True/False will display for few seconds if false
            }, }
        return notification

    # Get Shipment Data
    def get_shipment_data(self):
        url = "http://ubapimanagement.azure-api.net/trackandtrace/GetTrackAndTraceJSON?carrier={}&countryCode={}&barCode={}".format(
            self.carrier_id.number, self.country_code, self.bar_code)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        data = requests.get(url=url, headers=headers).json()
        if data['ErrorMessage'] != 'Error - Not found':
            # ----> Shipment Fields
            self.carrier = self.carrier_id.id
            self.carrier_weight = data['CarrierWeight']
            self.customer_reference = data['CustomerReference']
            self.delivery_date = data['DeliveryDate']
            self.information_source = data['InformationSource']
            self.lang_code = data['LangCode']
            self.order_number = data['OrderNumber']
            self.original_carrier = data['OriginalCarrier']
            self.package_number = data['PackageNumber']
            self.pickUp_date = data['PickUpDate']
            self.product = data['Product']
            self.weight = data['Weight']

            # ----> Receiver Info
            self.address = data['Receiver']['Address']
            self.business_name = data['Receiver']['BusinessName']
            self.city = data['Receiver']['City']
            self.contact_name = data['Receiver']['ContactName']
            self.zip = data['Receiver']['Zip']

            # ----> Scan Info
            scan_list = []
            for scan in data['Scans']:
                scan_list.append(
                    (0, 0, {'scan_code': scan['Code'], 'location': scan['Location'],
                            'scan_date': scan['ScanDate'], 'scan_text': scan['ScanText']})
                )
            self.scan_ids = [(5, 0, 0)]
            self.scan_ids = scan_list

            # ----> Sender Info
            self.senders_reference = data['SendersReference']
            self.signature_image = data['SignatureImage']
            self.signature_name = data['SignatureName']
            return self.show_notification('Done', 'Your shipment details have been successfully retrieved', 'success')
        else:
            return self.show_notification('Failed !',
                                          'Please make sure that the information entered is correct ',
                                          'danger')


class ScanLine(models.Model):
    _name = 'track.and.trace.scan.line'

    track_and_trace_id = fields.Many2one(comodel_name='track.and.trace', string='Track And Trace', required=False)
    scan_code = fields.Char('Code')
    location = fields.Char('Location')
    scan_date = fields.Char('Scan Date')
    scan_text = fields.Char('Scan Text')
