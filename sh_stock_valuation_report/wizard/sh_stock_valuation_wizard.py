# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api,_
import xlwt
from odoo.exceptions import UserError
import base64
import io
from datetime import datetime,timedelta
import json


class StockValuation(models.TransientModel):

    _name = 'sh.stock.valuation.wizard'
    _description = 'Stock Valuation Wizard'

    sh_from_date = fields.Date(string='Start Date', required=True)
    sh_to_date = fields.Date(string='End Date', required=True)
    sh_warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string='Warehouse', required=True)
    sh_company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True)
    sh_select_product_cat = fields.Selection([('product', 'Product'), (
        'category', 'Category')], string="Group BY Product - Category", default='product', required=True)
    sh_product_ids = fields.Many2many(
        comodel_name='product.product', string='Product', domain=[('type', '=', 'product'),('categ_id.property_cost_method','in',['standard','average'])])
    sh_category_ids = fields.Many2many(
        comodel_name='product.category', string='Category',domain=[('property_cost_method','in',['standard','average'])])
    sh_domain_warehouse = fields.Char(
        string='Domain', compute='_compute_location_domain', store=True)

    @api.onchange('sh_from_date', 'sh_to_date')
    def onchange_check_date(self):
        if self.sh_from_date and self.sh_to_date:
            if self.sh_from_date > self.sh_to_date:
                raise UserError('From date must be less than To date.')

    @api.depends('sh_warehouse_id', 'sh_company_id')
    def _compute_location_domain(self):
        for rec in self:
            sh_domain_ware = [('id', '<', 0)]
            ''' Compute For add domain in, location(Warehouse-wise)  '''
            if rec.sh_company_id:
                sh_domain_ware = [
                    ('company_id', '=', self.sh_company_id.id)]
            rec.sh_domain_warehouse = json.dumps(sh_domain_ware)


    def sh_print_stock_valuation_report(self):
        ''' PRINT PDF REPORT  '''
        datas = self.read()[0]
        res = self.env.ref(
            'sh_stock_valuation_report.sh_stock_valuation_report_action').report_action([], data=datas)
        return res

    def sh_prepare_stock_dict(self):
        '''  MAKE METHOD FOR PERPARE STOCK DICT IN ONE MATHOD 
            AND CALL THAT METHOD ON XLS REPORT AND VIEW REPORT 
        '''

        self.ensure_one()
        sh_current_date = datetime.today()
        sh_from_datetime=datetime.combine(self.sh_from_date, datetime.max.time())-timedelta(days=1)
        sh_to_datetime=datetime.combine(self.sh_to_date, datetime.max.time())
        
        stock_dict={}
        # ==============================================
        # CALCULATE PRODUCT WISE STOCK 
        #=============================================
        
        if self.sh_select_product_cat=='product':

            # ========================================================
            # CHECK PRODUCT SELECTED OR NOT IF SELECT THEN CALCULATE 
            # THAT PRODUCT STOCK ELSE CALCULATE ALL PRODUCT STOCK
            # ========================================================
            products=False
            if self.sh_product_ids:
                products=self.sh_product_ids
            else:
                category_ids=self.env['product.category'].sudo().search([('property_cost_method','in',['standard','average'])])
                self._cr.execute(''' select id from product_product where product_tmpl_id IN 
                    (select id from product_template where type='product' and categ_id in %s)
                    ''',[tuple(category_ids.ids)])
                products = self._cr.dictfetchall()
                products= self.env['product.product'].sudo().browse([r['id'] for r in products])
        
        # ====================================================
        # CALCULATE PRODUCT WISE STOCK WITH CATEGORY FILTER
        #=====================================================
        
        elif self.sh_select_product_cat=='category':
            if self.sh_category_ids:
                self._cr.execute(''' select id from product_product where product_tmpl_id IN 
                    (select id from product_template where type='product' and categ_id in %s) 
                    ''',[tuple(self.sh_category_ids.ids)]) 
                products = self._cr.dictfetchall()
                products= self.env['product.product'].sudo().browse([r['id'] for r in products])
            else:
                category_ids=self.env['product.category'].sudo().search([('property_cost_method','in',['standard','average'])])
                self._cr.execute(''' select id from product_product where product_tmpl_id IN 
                    (select id from product_template where type='product' and categ_id in %s) 
                    ''',[tuple(category_ids.ids)]) 
                products = self._cr.dictfetchall()
                products= self.env['product.product'].sudo().browse([r['id'] for r in products])
                
        if products:
            parent_location=[]
            warehouse_location=[]
            locations=self.env['stock.location'].search([('usage','=','internal')]) 
            for l in locations:
                if l.location_id:
                    current_location=l.location_id
                    while current_location.usage!='view' :
                        if current_location.location_id:
                            current_location=current_location.location_id
                    if current_location.id==self.sh_warehouse_id.view_location_id.id and current_location not in parent_location:
                        parent_location.append(current_location)  
            for pl in parent_location:        
                child_location=pl
                while child_location.child_ids :
                    if child_location.mapped('child_ids'):
                        warehouse_location+=child_location.mapped('child_ids').ids  
                        child_location=child_location.child_ids
            warehouse_location=[*set(warehouse_location)]
            
            
            
            
            # warehouse_location=self.env['stock.location'].search([('warehouse_id','=',self.sh_warehouse_id.id)])
            internal_location=warehouse_location
            # virtual_production_location=warehouse_location.filtered(lambda l:l.usage in ('inventory','production'))
            for product in products:
                
                # ====================================================
                # CALCULATE OPENING STOCK FOR PRODUCT WISE 
                # ====================================================
                
                # ====================================================
                # CALCULATE NEGATIVE TRANSFER QTY WHICH TRANSFTER FROM 
                # INTERNAL LOCATION TO INVENTORY LOCATION
                # ====================================================
                
                negative_qty_open=0
                positive_qty_open=0
                self._cr.execute('''select id,product_uom_qty from stock_move where product_id = %s and state='done' and date>=%s and date<=%s and scrapped = False 
                and location_id IN %s and location_dest_id IN (select id from stock_location where usage in ('inventory','production') and scrap_location=False ) ''',   
                [product.id,str(sh_from_datetime),str(sh_current_date),tuple(internal_location)])
                negative_qty_open = self._cr.dictfetchall()
                negative_qty_open=sum([sub['product_uom_qty'] for sub in negative_qty_open ])
                            
                # ====================================================
                # CALCULATE POSITIVE TRANSFER QTY WHICH TRANSFTER FROM 
                # INVENTORY LOCATION TO INTERNAL LOCATION
                # ====================================================   
                                
                self._cr.execute('''select id,product_uom_qty from stock_move where product_id = %s and state='done' and date>=%s and date<=%s and scrapped = False
                and location_id IN (select id from stock_location where usage in ('inventory','production') and scrap_location=False ) and location_dest_id IN %s''',   
                [product.id,str(sh_from_datetime),str(sh_current_date),tuple(internal_location)])
                positive_qty_open = self._cr.dictfetchall()
                positive_qty_open=sum([sub['product_uom_qty'] for sub in positive_qty_open ])
                            
                # ====================================================
                # CALCULATE PURCHASE QTY PRODUCT WISE 
                # ==================================================== 
                                
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and location_dest_id in %s
                and move_id IN ( select id from stock_move where product_id = %s and state='done' and date>=%s and date<=%s and scrapped = False) 
                and picking_id IN (select id from stock_picking where picking_type_id IN ( select id from stock_picking_type where code='incoming'))''',   
                [product.id,str(sh_from_datetime),str(sh_current_date),tuple(internal_location),product.id,str(sh_from_datetime),str(sh_current_date)])
                purchase_qty_open = self._cr.dictfetchall()
                purchase_qty_open=sum([sub['qty_done'] for sub in purchase_qty_open ])
                
                # ====================================================
                # CALCULATE SALE QTY PRODUCT WISE 
                # ==================================================== 
                
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and location_id in %s
                and move_id IN ( select id from stock_move where product_id = %s and state='done' and date>=%s and date<=%s and scrapped = False) 
                and picking_id IN (select id from stock_picking where picking_type_id IN ( select id from stock_picking_type where code='outgoing'))''',   
                [product.id,str(sh_from_datetime),str(sh_current_date),tuple(internal_location),product.id,str(sh_from_datetime),str(sh_current_date)])
                sale_qty_open = self._cr.dictfetchall()
                sale_qty_open=sum([sub['qty_done'] for sub in sale_qty_open ])

                # ====================================================
                # CALCULATE CURRENT ONAND QTY FROM STOCK QUANT
                # ==================================================== 
                
                self._cr.execute('''select id,quantity from stock_quant where product_id = %s and location_id IN %s ''',[product.id,tuple(internal_location)])
                onhand = self._cr.dictfetchall()
                onhand=sum([sub['quantity'] for sub in onhand ])

                # ====================================================
                # CALCULATE SCRAP QTY WHICH ARE TRANSFER FROM INTERNAL 
                # LOCATION TO SCRAP LOCATION
                # ==================================================== 
                
                scrap_qty_open=0
                self._cr.execute('''select id,product_uom_qty from stock_move where product_id = %s and state='done' and date>=%s and date<=%s and scrapped = True 
                and location_id IN %s and location_dest_id IN (select id from stock_location where usage in ('inventory','supplier','customer','production') and scrap_location=True) ''',   
                [product.id,str(sh_from_datetime),str(sh_current_date),tuple(internal_location)])
                scrap_qty_open = self._cr.dictfetchall()
                scrap_qty_open=sum([sub['product_uom_qty'] for sub in scrap_qty_open ])
                
                # ==============================================================
                # CALCULATE QTY TRANSFER FROM SELECTED WAREHOUSE TO OTHER 
                # WAREHOUSE & OTHER WAREHOUSE TO SELECTED WAREHOUSE
                # ==============================================================
                
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and 
                    picking_id in ( select id from stock_picking where picking_type_id in (select id from stock_picking_type where code = 'internal') and 
                    location_id in (select id from stock_location where usage='internal' and id not in %s ) and 
                    location_dest_id in (select id from stock_location where usage='internal' and id in %s)) ''',   
                [product.id,str(sh_from_datetime),str(sh_current_date),tuple(internal_location),tuple(internal_location)])
                positive_transfer_open = self._cr.dictfetchall()
                positive_transfer_open=sum([sub['qty_done'] for sub in positive_transfer_open ])
                
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and 
                    picking_id in ( select id from stock_picking where picking_type_id in (select id from stock_picking_type where code = 'internal') and 
                    location_id in (select id from stock_location where usage='internal' and id in %s) and 
                    location_dest_id in (select id from stock_location where usage='internal' and id not in %s )) ''',   
                [product.id,str(sh_from_datetime),str(sh_current_date),tuple(internal_location),tuple(internal_location)])
                negative_transfer_open= self._cr.dictfetchall()
                negative_transfer_open=sum([sub['qty_done'] for sub in negative_transfer_open ])
                transfer_qty_open=positive_transfer_open-negative_transfer_open
                
                
                # ====================================================
                # CALCULATE OPENIG STOCK USING ABOVE QTY
                # ==================================================== 
                
                open_stock= onhand-purchase_qty_open+sale_qty_open - positive_qty_open+negative_qty_open+scrap_qty_open-transfer_qty_open
    
                # ====================================================
                # CALCULATE CLOSING STOCK FOR PRODUCT WISE 
                # ====================================================
                    
                # ====================================================
                # CALCULATE NEGATIVE TRANSFER QTY WHICH TRANSFTER FROM 
                # INTERNAL LOCATION TO INVENTORY LOCATION
                # ====================================================
                    
                negative_qty_close=0
                positive_qty_close=0
                self._cr.execute('''select id,product_uom_qty from stock_move where product_id = %s and state='done' and date>=%s and date<=%s and scrapped = False
                and location_id IN %s and location_dest_id IN (select id from stock_location where usage in ('inventory','production') and scrap_location=False) ''',   
                [product.id,str(sh_to_datetime),str(sh_current_date),tuple(internal_location)])
                negative_qty_close = self._cr.dictfetchall()
                negative_qty_close=sum([sub['product_uom_qty'] for sub in negative_qty_close ])
                                
                # ====================================================
                # CALCULATE POSITIVE TRANSFER QTY WHICH TRANSFTER FROM 
                # INVENTORY LOCATION TO INTERNAL LOCATION
                # ==================================================== 
                                
                self._cr.execute('''select id,product_uom_qty from stock_move where product_id = %s and state='done' and date>=%s and date<=%s and scrapped = False
                and location_id IN (select id from stock_location where usage in ('inventory','production') and scrap_location=False ) and location_dest_id IN %s ''',   
                [product.id,str(sh_to_datetime),str(sh_current_date),tuple(internal_location)])
                positive_qty_close = self._cr.dictfetchall()
                positive_qty_close=sum([sub['product_uom_qty'] for sub in positive_qty_close ])
                                
                # ====================================================
                # CALCULATE PURCHASE QTY PRODUCT WISE 
                # ==================================================== 
                                    
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and location_dest_id in %s
                and move_id IN ( select id from stock_move where product_id = %s and state='done' and date>=%s and date<=%s and scrapped = False) 
                and picking_id IN (select id from stock_picking where picking_type_id IN ( select id from stock_picking_type where code='incoming'))''',   
                [product.id,str(sh_to_datetime),str(sh_current_date),tuple(internal_location),product.id,str(sh_to_datetime),str(sh_current_date)])
                purchase_qty_close = self._cr.dictfetchall()
                purchase_qty_close=sum([sub['qty_done'] for sub in purchase_qty_close ])
            
                # ====================================================
                # CALCULATE SALE QTY PRODUCT WISE 
                # ==================================================== 
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and location_id in %s
                and move_id IN ( select id from stock_move where product_id = %s and state='done' and date>=%s and date<=%s and scrapped = False) 
                and picking_id IN (select id from stock_picking where picking_type_id IN ( select id from stock_picking_type where code='outgoing'))''',   
                [product.id,str(sh_to_datetime),str(sh_current_date),tuple(internal_location),product.id,str(sh_to_datetime),str(sh_current_date)])
                sale_qty_close = self._cr.dictfetchall()
                sale_qty_close=sum([sub['qty_done'] for sub in sale_qty_close ])

                # ====================================================
                # CALCULATE SCRAP QTY WHICH ARE TRANSFER FROM INTERNAL 
                # LOCATION TO SCRAP LOCATION
                # ==================================================== 
                scrap_qty_close=0
                self._cr.execute('''select id,product_uom_qty from stock_move where product_id = %s and state='done' and date>=%s and date<=%s and scrapped = True
                and location_id IN %s and location_dest_id IN (select id from stock_location where usage in ('inventory','supplier','customer','production') and scrap_location=True) ''',   
                [product.id,str(sh_to_datetime),str(sh_current_date),tuple(internal_location)])
                scrap_qty_close = self._cr.dictfetchall()
                scrap_qty_close=sum([sub['product_uom_qty'] for sub in scrap_qty_close ])

                #  ==============================================================
                # CALCULATE QTY TRANSFER FROM SELECTED WAREHOUSE TO OTHER 
                # WAREHOUSE & OTHER WAREHOUSE TO SELECTED WAREHOUSE
                # ==============================================================
                
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and 
                    picking_id in ( select id from stock_picking where picking_type_id in (select id from stock_picking_type where code = 'internal') and 
                    location_id in (select id from stock_location where usage='internal' and id not in %s) and 
                    location_dest_id in (select id from stock_location where usage='internal' and id in %s)) ''',   
                [product.id,str(sh_to_datetime),str(sh_current_date),tuple(internal_location),tuple(internal_location)])
                positive_transfer_close = self._cr.dictfetchall()
                positive_transfer_close=sum([sub['qty_done'] for sub in positive_transfer_close ])
                
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and 
                    picking_id in ( select id from stock_picking where picking_type_id in (select id from stock_picking_type where code = 'internal') and 
                    location_id in (select id from stock_location where usage='internal' and id in %s) and 
                    location_dest_id in (select id from stock_location where usage='internal' and id not in %s)) ''',   
                [product.id,str(sh_to_datetime),str(sh_current_date),tuple(internal_location),tuple(internal_location)])
                negative_transfer_close= self._cr.dictfetchall()
                negative_transfer_close=sum([sub['qty_done'] for sub in negative_transfer_close ])
                transfer_qty_close=positive_transfer_close-negative_transfer_close
                
                # ====================================================
                # CALCULATE CLOSING STOCK USING ABOVE QTY
                # ==================================================== 
                
                close_stock= onhand-purchase_qty_close+sale_qty_close - positive_qty_close+negative_qty_close+scrap_qty_close-transfer_qty_close    
                
                # ====================================================
                # CALCULATE NEGATIVE ADJUSTMENT QTY WHICH ARE TRANSFER 
                # FROM INTERNAL LOCATION TO INVENTORY LOCATION
                # ==================================================== 
                negative_qty_adjustment=0
                positive_qty_adjustment=0
               
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and picking_id IS NULL
                and location_id IN %s and location_dest_id IN (select id from stock_location where usage in ('inventory') and scrap_location=False) ''',   
                [product.id,str(sh_from_datetime),str(sh_to_datetime),tuple(internal_location)])
                negative_qty_adjustment = self._cr.dictfetchall()
                negative_qty_adjustment=sum([sub['qty_done'] for sub in negative_qty_adjustment ])
                            
                # ====================================================
                # CALCULATE POSITIVE ADJUSTMENT QTY WHICH ARE TRANSFER 
                # FROM INVENTORY LOCATION TO INTERNAL LOCATION
                # ====================================================                 
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and picking_id IS NULL
                and location_id IN (select id from stock_location where usage in ('inventory') and scrap_location=False) and location_dest_id IN %s ''',   
                [product.id,str(sh_from_datetime),str(sh_to_datetime),tuple(internal_location)])
                positive_qty_adjustment = self._cr.dictfetchall()
                positive_qty_adjustment=sum([sub['qty_done'] for sub in positive_qty_adjustment ])
                
                # ==============================================================
                # CALCULATE TOTAL ADJUSTMENT DONE BETWEEN FROM DATE TO TO DATE 
                # ==============================================================
                adjustment=positive_qty_adjustment-negative_qty_adjustment
                
                # ==============================================================
                # CALCULATE SALE QUANTITY BETWEEN FROM DATE <--> TO DATE
                # ==============================================================
                
                sale_qty=sale_qty_open-sale_qty_close
                
                # ==============================================================
                # CALCULATE PURCHASE QUANTITY BETWEEN FROM DATE <--> TO DATE
                # ==============================================================
                
                purchase_qty=purchase_qty_open-purchase_qty_close
                
                # ==============================================================
                # CALCULATE QTY TRANSFER FROM SELECTED WAREHOUSE TO OTHER 
                # WAREHOUSE & OTHER WAREHOUSE TO SELECTED WAREHOUSE
                # ==============================================================
                
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and 
                    picking_id in ( select id from stock_picking where picking_type_id in (select id from stock_picking_type where code = 'internal') and 
                    location_id in (select id from stock_location where usage='internal' and id not in %s) and 
                    location_dest_id in %s) ''',   
                [product.id,str(sh_from_datetime),str(sh_to_datetime),tuple(internal_location),tuple(internal_location)])
                positive_transfer = self._cr.dictfetchall()
                positive_transfer=sum([sub['qty_done'] for sub in positive_transfer ])
                
                self._cr.execute('''select id,qty_done from stock_move_line where product_id = %s and state='done' and date>=%s and date<=%s and 
                    picking_id in ( select id from stock_picking where picking_type_id in (select id from stock_picking_type where code = 'internal') and 
                    location_id in %s and 
                    location_dest_id in (select id from stock_location where usage='internal' and id not in %s )) ''',   
                [product.id,str(sh_from_datetime),str(sh_to_datetime),tuple(internal_location),tuple(internal_location)])
                negative_transfer = self._cr.dictfetchall()
                negative_transfer=sum([sub['qty_done'] for sub in negative_transfer ])
                
                transfer_qty=positive_transfer-negative_transfer
                
                # ===============================================================
                # CALCULATE COSTING & STOCK VALUATION OF PRODUCT AT END DATE 
                # FROM STOCK VALUATION LAYER
                # ===============================================================
                
                self._cr.execute('''select id,quantity,value,unit_cost from stock_valuation_layer where product_id = %s and create_date<=%s  and company_id=%s ''',   
                [product.id,str(sh_to_datetime),self.sh_warehouse_id.company_id.id])
                stock_valuation = self._cr.dictfetchall()
                valuation=sum([sub['value'] for sub in stock_valuation ])
                
                # ===============================================================
                # CALCULATE COSTING FROM VALUATION / END STOCK 
                # ===============================================================
                if close_stock and valuation:
                    costing=round(valuation/close_stock,2)
                else:
                    costing=0
                    
                # ===============================================================
                # ADD ALL CALCULATE VALUES IN LIST AND THAT LIST ADDED TO ONE 
                # DICT WHICH MANAGE BY PRODUCT DISPLAY NAME  
                # ===============================================================    
                stock_dict[product.display_name]=[product.default_code,product,product.categ_id,
                    open_stock,sale_qty,purchase_qty,adjustment,transfer_qty,close_stock,costing,valuation]
                
        return stock_dict

    def sh_view_stock_valuation_report(self):
        ''' 
            MAKE VIEW REPORT 
        '''
        # ========================================================
        # DELETE ALL PREVIOUSE RECORD IN STOCK VALUATION VIEW
        # ========================================================
        
        self._cr.execute(""" DELETE FROM sh_stock_valuation""")
        
        # ===================================================
        # CALL METHOD TO PREPARE STOCK DICT TO PRINT REPORT
        # ===================================================
        
        
        stock_dict=self.sh_prepare_stock_dict()
            
        if stock_dict:    
            for product in stock_dict.keys():
                self.env['sh.stock.valuation'].create({
                    'default_code' : stock_dict[product][0],
                    'product_id' : stock_dict[product][1].id,
                    'categ_id' : stock_dict[product][2].id,
                    'sh_open_stock' : stock_dict[product][3],
                    'sh_sale_qty':stock_dict[product][4],
                    'sh_purchase_qty' : stock_dict[product][5],
                    'sh_adjustment_qty' : stock_dict[product][6],
                    'sh_transfer_qty' : stock_dict[product][7],
                    'sh_close_stock' : stock_dict[product][8],
                    'sh_costing':stock_dict[product][9],
                    'sh_valuation' : stock_dict[product][10],
                })    
        return {
            'name': 'Stock Valuation Report',
            'type': 'ir.actions.act_window',
            'res_model': 'sh.stock.valuation',
            'view_mode': 'tree',
            'view_id': self.env.ref('sh_stock_valuation_report.sh_stock_valuation_view_tree').id,
            } 
            

    def sh_xls_stock_valuation_report(self):
        ''' 
            PRINT XLS REPORT 
        '''
        
        # ===================================================
        # CALL METHOD TO PREPARE STOCK DICT TO PRINT REPORT
        # ===================================================
        stock_dict=self.sh_prepare_stock_dict()
            
        if stock_dict:    
            ############################## XLS REPORT ###################################
            # ============================
            # Get Value
            # ============================

            workbook = xlwt.Workbook()
            heading_font_with_background = xlwt.easyxf(
            'font:height 230,bold True;align: vert center;align:wrap on, horiz center;pattern: pattern solid,fore_colour gray25;')
            heading_font = xlwt.easyxf(
                'font:height 210,bold True;align: vert center;align: horiz center;')
            normal_text = xlwt.easyxf(
                'font:bold False,color black;align: horiz center;align: vert center;')

            worksheet = workbook.add_sheet(
                'STOCK VALUATION REPORT', heading_font_with_background)

            worksheet.col(0).width = 3000
            worksheet.col(1).width = 9000
            worksheet.col(2).width = 6000
            worksheet.col(3).width = 3000
            worksheet.col(4).width = 3000
            worksheet.col(5).width = 3000
            worksheet.col(6).width = 3100
            worksheet.col(7).width = 3100
            worksheet.col(8).width = 3100
            worksheet.col(9).width = 3000
            worksheet.col(10).width = 3000
            worksheet.col(11).width = 3000
            
            # =======================================================
            # PRINT REPORT HEADING IN XLS 
            # =======================================================
            
            worksheet.write_merge(1, 1, 1, 8, 'STOCK VALUATION REPORT', heading_font_with_background)
            worksheet.write_merge(3, 3, 1, 1, 'START DATE', heading_font_with_background)
            worksheet.write_merge(3, 3, 2, 2, 'END DATE', heading_font_with_background)
            worksheet.write_merge(3, 3, 3, 5, 'COMPANY',heading_font_with_background)
            worksheet.write_merge(3, 3, 6, 8, 'WAREHOUSE ', heading_font_with_background)
            worksheet.write_merge(4, 4, 1, 1, str(self.sh_from_date), heading_font)
            worksheet.write_merge(4, 4, 2, 2, str(self.sh_to_date),heading_font)
            worksheet.write_merge(4, 4, 3, 5, self.sh_company_id.name,heading_font)
            worksheet.write_merge(4, 4, 6, 8,self.sh_warehouse_id.name,heading_font)

            # =======================================================
            # PRINT REPORT COLUMNS HEADERS
            # =======================================================

            worksheet.write_merge(6, 7, 0, 0, 'Default Code', heading_font_with_background)
            worksheet.write_merge(6, 7, 1, 1, 'Product Name', heading_font_with_background)
            worksheet.write_merge(6, 7, 2, 2, 'Category Name', heading_font_with_background)
            worksheet.write_merge(6, 7, 3, 3, 'Opening Stock', heading_font_with_background)
            worksheet.write_merge(6, 7, 4, 4, 'Sales', heading_font_with_background)
            worksheet.write_merge(6, 7, 5, 5, 'Purchase', heading_font_with_background)
            worksheet.write_merge(6, 7, 6, 6, 'Adjustment', heading_font_with_background)
            worksheet.write_merge(6, 7, 7, 7, 'Internal Transfer', heading_font_with_background)
            worksheet.write_merge(6, 7, 8, 8, 'Closing Stock', heading_font_with_background)
            worksheet.write_merge(6, 7, 9, 9, 'Costing', heading_font_with_background)
            worksheet.write_merge(6, 7, 10, 10, 'Valuation', heading_font_with_background)

            # =======================================================
            # PRINT XLS REPORT PRODUCT WISE FROM DICT
            # =======================================================
            
            line_var=9
            if stock_dict:
                for product in stock_dict.keys():
                   
                    worksheet.write_merge(
                        line_var, line_var, 0, 0, stock_dict[product][0], normal_text)
                    worksheet.write_merge(
                        line_var, line_var, 1, 1, stock_dict[product][1].display_name, normal_text)
                    worksheet.write_merge(
                        line_var, line_var, 2, 2, stock_dict[product][2].display_name, normal_text)
                    worksheet.write_merge(
                        line_var, line_var, 3, 3, stock_dict[product][3], normal_text)
                    worksheet.write_merge(
                        line_var, line_var, 4, 4, stock_dict[product][4], normal_text)
                    worksheet.write_merge(
                        line_var, line_var, 5, 5, stock_dict[product][5], normal_text)
                    worksheet.write_merge(
                        line_var, line_var, 6, 6, stock_dict[product][6], normal_text)
                    worksheet.write_merge(
                        line_var, line_var, 7, 7, stock_dict[product][7], normal_text)
                    worksheet.write_merge(
                        line_var, line_var, 8, 8, stock_dict[product][8], normal_text)
                    worksheet.write_merge(
                        line_var, line_var, 9, 9, stock_dict[product][9], normal_text)
                    worksheet.write_merge(
                        line_var, line_var, 10, 10, stock_dict[product][10], normal_text)
                    line_var += 1
        else:
            raise UserError(_('No Records Found.....'))


        fp = io.BytesIO()
        workbook.save(fp)
        data = base64.encodebytes(fp.getvalue())
        IrAttachment = self.env['ir.attachment']
        attachment_vals = {
            "name": "STOCK_VALUATION_REPORT.xls",
            "res_model": "ir.ui.view",
            "type": "binary",
            "datas": data,
            "public": True,
        }
        fp.close()

        attachment = IrAttachment.search([('name', '=', 'STOCK_VALUATION_REPORT'),
                                          ('type', '=', 'binary'),
                                          ('res_model', '=', 'ir.ui.view')],
                                         limit=1)
        if attachment:
            attachment.write(attachment_vals)
        else:
            attachment = IrAttachment.create(attachment_vals)
        # TODO: make user error here
        if not attachment:
            raise UserError('There is no attachments...')

        url = "/web/content/" + str(attachment.id) + "?download=true"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
