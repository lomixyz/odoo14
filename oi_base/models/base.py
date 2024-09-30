'''
Created on Sep 18, 2018

@author: Zuhair Hammadi
'''
from odoo import models, api, fields
import datetime
import re
import uuid

def normilize(*names):
    name = ' '.join(filter(None,names))
    return re.sub('\W',' ', name.lower()).strip().replace(' ', '_')     

class Base(models.AbstractModel):
    _inherit ='base'
    
    @api.model
    def _base(self, model = 'base'):
        return type(self.env[model])
        
    def _read_field(self, field):
        """
        :param field name
        :return: dictionary mapping record id with field value
        """
        res = self.read([field])
        res = {record['id'] : record[field] for record in res}
        return res
    
    def _suggest_external_id(self):
        if self._name =='ir.model.fields':
            return normilize(self._name, self.model, self.name) 
        return normilize(self._name, 'code' in self and isinstance(self['code'], str) and len(self['code']) < 20 and self['code'] or '', self.display_name)
    
    def _create_external_id(self):
        ref = self.get_external_id().get(self.id)        
        if not ref:
            IrModelData = self.env['ir.model.data']
            if self._context.get('is_approval_setting'):
                vals = {'module' : '_workflow',
                        'name' : normilize(self._name, 'code' in self and isinstance(self['code'], str) and len(self['code']) < 20 and self['code'] or '', self.display_name),
                        'noupdate' : True
                    }
            else:
                vals = {'module' : '_',
                        'name' : normilize(self._name, 'code' in self and isinstance(self['code'], str) and len(self['code']) < 20 and self['code'] or '', self.display_name)
                    }
            while IrModelData.search(self._dict_to_domain(vals)):
                vals['name'] = '%s_%s' % (vals['name'], uuid.uuid4().hex[:6])            
            vals.update({
                'model' : self._name,
                'res_id' : self.id
                })
            ref=IrModelData.create(vals).complete_name     
        return ref       
        
    @api.model
    def _isinstance(self, model):
        return isinstance(self, type(self.env[model]))
    
    @api.model
    def _get_sql_value(self, sql, para = ()):
        self._cr.execute(sql, para)
        res=self._cr.fetchone()
        res= res and res[0] or False
        if isinstance(res, datetime.datetime):
            return fields.Datetime.to_string(res)
        if isinstance(res, datetime.date):
            return fields.Date.to_string(res)
        return res     
    
    @api.model
    def _dict_to_domain(self, vals):
        domain = []
        for key, value in vals.items():
            if isinstance(value, (dict,list,tuple )):
                value = str(value)
            domain.append((key, '=', value))
        return domain
    
    def get_title(self):        
        return '%s | %s' % (self.env['ir.model']._get(self._name).name, self.display_name)    
    
    def get_form_url(self):
        return '/web#id=%d&model=%s&view_type=form' % (self.id, self._name)
        
    def _expand_group_all(self, records, domain, order):
        return records.search([], order = order)

    def onchange(self, values, field_name, field_onchange):
        self = self.with_context(onchange_field_name = field_name, onchange_model = self._name)
        return super(Base, self).onchange(values, field_name, field_onchange)        
    
    def _onchange_eval(self, field_name, onchange, result):
        self = self.with_context(onchange_eval_field_name = field_name)
        return super(Base, self)._onchange_eval(field_name, onchange, result)       
    
    def _hierarchical_sort(self, parent_name = None):
        parent_name = parent_name or self._parent_name or 'parent_id'
        vals = {}
        for record in self:
            parent = record
            level = 0
            recursion_test = set()
            while parent[parent_name]:
                level +=1
                parent = parent[parent_name]
                if parent in recursion_test:
                    break
                recursion_test.add(parent)
            vals[record] = level
            
        return self.sorted(key = lambda record : (vals[record], record.display_name))
    
    def _selection_name(self, field_name):
        if not self:
            return False
        names = dict(self._fields[field_name]._description_selection(self.env))
        value = self[field_name]
        return names.get(value, value)   
    
    def check_access_rule(self, operation):
        if not any(self.ids):
            return
        return super(Base, self).check_access_rule(operation)
    
    def _action_view_one2many(self, field_name):
        field = self._fields[field_name]
        assert field.type == 'one2many'
        return {
            'type' : 'ir.actions.act_window',
            'name' : self.env['ir.model.fields']._get(self._name, field.name).field_description,
            'res_model' : field.comodel_name, 
            'view_mode' : 'tree,form',
            'domain' : [(field.inverse_name,'=', self.id)],
            'context' : {
                'default_' + field.inverse_name : self.id
                }
            }    