# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, api,_
from datetime import date, datetime,timedelta
from odoo.exceptions import UserError

class StockValuationReport(models.AbstractModel):
    _name = 'report.sh_stock_valuation_report.sh_stock_valuation_template'
    _description = 'Stock Valuation Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        ''' Prepare values for print stock card report'''
        data = dict(data or {})

        # Getting Value form wizard

        sh_from_date = datetime.strptime(
            data['sh_from_date'], '%Y-%m-%d').date()
        sh_to_date = datetime.strptime(
            data['sh_to_date'], '%Y-%m-%d').date()
        sh_company_id = self.env['res.company'].sudo().search(
            [('id', '=', data.get('sh_company_id')[0])])
        sh_warehouse_id = self.env['stock.warehouse'].sudo().search(
            [('id', '=', data.get('sh_warehouse_id')[0])])
        sh_current_date = datetime.today()
        sh_from_datetime=datetime.combine(sh_from_date, datetime.max.time())-timedelta(days=1)
        sh_to_datetime=datetime.combine(sh_to_date, datetime.max.time())
        sh_category_ids = data.get('sh_category_ids')
        sh_product_ids = data.get('sh_product_ids')
        sh_select_product_cat = data.get('sh_select_product_cat')
        
        stock_dict={}
        # ==============================================
        # CALCULATE PRODUCT WISE STOCK 
        #=============================================
        
        if sh_select_product_cat=='product':

            # ========================================================
            # CHECK PRODUCT SELECTED OR NOT IF SELECT THEN CALCULATE 
            # THAT PRODUCT STOCK ELSE CALCULATE ALL PRODUCT STOCK
            # ========================================================
            products=False
            if sh_product_ids:
                products=self.env['product.product'].sudo().browse([r for r in sh_product_ids])
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
        
        elif sh_select_product_cat=='category':
            if sh_category_ids:
                self._cr.execute(''' select id from product_product where product_tmpl_id IN 
                    (select id from product_template where type='product' and categ_id in %s) 
                    ''',[tuple(sh_category_ids)]) 
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
                    if current_location.id==sh_warehouse_id.view_location_id.id and current_location not in parent_location:
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
                and location_id IN (select id from stock_location where usage in ('inventory','production')  and scrap_location=False ) and location_dest_id IN %s''',   
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
                and location_id IN %s and location_dest_id IN (select id from stock_location where usage in ('inventory','supplier','customer','production')  and scrap_location=True) ''',   
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
                and location_id IN %s and location_dest_id IN (select id from stock_location where usage IN ('inventory','supplier','customer','production') and scrap_location=True) ''',   
                [product.id,str(sh_to_datetime),str(sh_current_date),tuple(internal_location)])
                scrap_qty_close = self._cr.dictfetchall()
                scrap_qty_close=sum([sub['product_uom_qty'] for sub in scrap_qty_close ])

                # ==============================================================
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
                
                self._cr.execute('''select id,quantity,value,unit_cost from stock_valuation_layer where product_id = %s and create_date<=%s and company_id=%s ''',   
                [product.id,str(sh_to_datetime),sh_warehouse_id.company_id.id])
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
                stock_dict[product.display_name]=[product.default_code,product.display_name,product.categ_id.display_name,
                    round(open_stock,2),sale_qty,purchase_qty,adjustment,transfer_qty,close_stock,costing,round(valuation,2)]
                
            
        # Return Preparing values
        if stock_dict:
            return{
                'sh_from_date': sh_from_date,
                'sh_to_date': sh_to_date,
                'stock_dict': stock_dict,
                'sh_company_id':sh_company_id.name,
                'sh_warehouse_id': sh_warehouse_id.name,
                'sh_select_product_cat': sh_select_product_cat,
            }
        else:
            raise UserError(_('No Records Found.....'))