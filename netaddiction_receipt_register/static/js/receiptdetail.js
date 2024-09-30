odoo.define('netaddiction_receipt_register.receiptdetail', function (require) {
  "use strict";

  var core = require('web.core');
  var Widget = require('web.Widget');
  var AbstractAction = require('web.AbstractAction');


  core.qweb.add_template("/netaddiction_receipt_register/static/xml/receipt_detail.xml");

  function parseDate(input) {
    var parts = input.split('-');
    return parts[2].substring(0, 2);
  }

  var receiptDetail = AbstractAction.extend({
    init: function (parent, action, options) {
      this._super.apply(this, arguments);
      this.action = action;
      this.action_manager = parent;
    },
    start: function () {
      this._super.apply(this, arguments);
      var self = this;
      let list = new receiptDetailHome(self);
      self.$el.html('');
      list.appendTo(self.$el);
    },
  });

  var receiptDetailHome = Widget.extend({
    template: 'vatregister_top',
    events: {
      "click #search": "_get_receipt",
      "click #products": "_filter_products",
      'click #total': "_filter_total",
      'click #multiplayer': "_filter_multiplayer",
      'click #days': "_filter_days",
      'click #categ_group': "_filter_category"
    },
    init: function () {
      this._super.apply(this, arguments);
      this.year = []
      this.pickings = []
      var current_year = parseInt(new Date().getFullYear());
      var first_year = parseInt(2000)

      while (first_year <= current_year) {
        this.year.push({ 'value': current_year, 'name': current_year });
        current_year = current_year - 1
      }
    },
    _get_receipt: function (e) {
      e.preventDefault();
      var self = this;
      var year = parseInt($('#year').val());
      var month = parseInt($('#month').val());

      return self._rpc({
        model: 'stock.picking',
        method: 'get_picking_from_date',
        args: [year, month]
      }).then((pickings) => {
        self.pickings = pickings
        $('#content_vatregister').html('')

        var receiptTotal = new total(null, pickings);
        return receiptTotal.appendTo('#content_vatregister');
      })
    },
    _filter_products: function (e) {
      $('#content_vatregister').html('');
      var prod = new products(null, this.pickings);
      return prod.appendTo('#content_vatregister');
    },
    _filter_total: function (e) {
      $('#content_vatregister').html('');
      var t = new total(null, this.pickings);
      return t.appendTo('#content_vatregister');
    },
    _filter_multiplayer: function (e) {
      $('#content_vatregister').html('');
      var t = new multiplayer(null, this.pickings);
      return t.appendTo('#content_vatregister');
    },
    _filter_days: function (e) {
      $('#content_vatregister').html('');
      var t = new days(null, this.pickings);
      return t.appendTo('#content_vatregister');
    },
    _filter_category: function (e) {
      $('#content_vatregister').html('');
      var t = new categ(null, this.pickings);
      return t.appendTo('#content_vatregister');
    }
  });

  var total = Widget.extend({
    template: 'table_vatregister_total',
    init: function (parent, pickings) {
      this.pickings = {
        'done': {
          qty: 0,
          taxed: 0,
          tax: 0,
          name_tax: { 'Edizioni': 0 },
          order_qty: 0
        }, 'refund': {
          qty: 0,
          taxed: 0,
          tax: 0,
          name_tax: { 'Edizioni': 0 },
          order_qty: 0
        }
      };
      var picks = this.pickings;
      var order = [];
      $(pickings.done).each(function (index, value) {
        order.push(value.sale_id)
        picks['done']['qty'] = picks['done']['qty'] + parseInt(value.qty);
        picks['done']['taxed'] = parseFloat(picks['done']['taxed']) + parseFloat(value.total_price);
        picks['done']['tax'] = parseFloat(picks['done']['tax']) + parseFloat(value.price_tax);
        picks['done']['name_tax']['Edizioni'] = parseFloat(picks['done']['name_tax']['Edizioni']) + parseFloat(value.edizioni);
        if (value.tax_id in picks['done']['name_tax']) {
          picks['done']['name_tax'][value.tax_id] = parseFloat(picks['done']['name_tax'][value.tax_id]) + parseFloat(value.price_tax);
        } else {
          picks['done']['name_tax'][value.tax_id] = parseFloat(value.price_tax);
        }
        picks['done']['name_tax'][value.tax_id] = parseFloat(picks['done']['name_tax'][value.tax_id]).toFixed(2)

      });
      var refund_order = [];
      $(pickings.refund).each(function (index, value) {
        refund_order.push(value.sale_id)
        picks['refund']['qty'] = picks['refund']['qty'] + parseInt(value.qty);
        picks['refund']['taxed'] = parseFloat(picks['refund']['taxed']) + parseFloat(value.total_price);
        picks['refund']['tax'] = parseFloat(picks['refund']['tax']) + parseFloat(value.price_tax);
        picks['refund']['name_tax']['Edizioni'] = parseFloat(picks['refund']['name_tax']['Edizioni']) + parseFloat(value.edizioni);
        if (value.tax_id in picks['refund']['name_tax']) {
          picks['refund']['name_tax'][value.tax_id] = parseFloat(picks['refund']['name_tax'][value.tax_id]) + parseFloat(value.price_tax);
        } else {
          picks['refund']['name_tax'][value.tax_id] = parseFloat(value.price_tax);
        }
        picks['refund']['name_tax'][value.tax_id] = parseFloat(picks['refund']['name_tax'][value.tax_id]).toFixed(2)
      });
      refund_order = $.unique(refund_order);
      order = $.unique(order);
      picks['refund']['order_qty'] = refund_order.length
      picks['done']['order_qty'] = order.length

      picks['refund']['taxed'] = parseFloat(picks['refund']['taxed']).toFixed(2)
      picks['refund']['tax'] = parseFloat(picks['refund']['tax']).toFixed(2)
      picks['refund']['name_tax']['Edizioni'] = parseFloat(picks['refund']['name_tax']['Edizioni']).toFixed(2)

      picks['done']['taxed'] = parseFloat(picks['done']['taxed']).toFixed(2)
      picks['done']['tax'] = parseFloat(picks['done']['tax']).toFixed(2)
      picks['done']['name_tax']['Edizioni'] = parseFloat(picks['done']['name_tax']['Edizioni']).toFixed(2)

      this.pickings = picks;
    }
  });

  var categ = Widget.extend({
    template: 'table_vatregister_categ',
    init: function (parent, pickings) {
      this.pickings = { 'done': {}, 'refund': {} }
      var total_price = 0;
      var price_tax = 0;
      var edizioni = 0;
      var picks = this.pickings;
      $(pickings.done).each(function (index, value) {
        total_price = total_price + parseFloat(value.total_price);
        price_tax = price_tax + parseFloat(value.price_tax);
        edizioni = edizioni + parseFloat(value.edizioni);
        var categ = value.categ;
        if (categ in picks['done']) {
          picks['done'][categ]['qty'] = picks['done'][categ]['qty'] + parseInt(value.qty)
          picks['done'][categ]['total_price'] = parseFloat(picks['done'][categ]['total_price']) + parseFloat(value.total_price)
          picks['done'][categ]['price_tax'] = parseFloat(picks['done'][categ]['price_tax']) + parseFloat(value.price_tax)
          picks['done'][categ]['edizioni'] = parseFloat(picks['done'][categ]['edizioni']) + parseFloat(value.edizioni)
          picks['done'][categ]['order'].push(value.sale_id)
        } else {
          picks['done'][categ] = {
            'qty': parseInt(value.qty),
            'total_price': parseFloat(value.total_price),
            'price_tax': parseFloat(value.price_tax),
            'edizioni': parseFloat(value.edizioni),
            'order': [value.sale_id]
          }
        }
        picks['done'][categ]['order'] = $.unique(picks['done'][categ]['order']);
        picks['done'][categ]['qty_order'] = picks['done'][categ]['order'].length
        picks['done'][categ]['total_price'] = parseFloat(picks['done'][categ]['total_price']).toFixed(2)
        picks['done'][categ]['price_tax'] = parseFloat(picks['done'][categ]['price_tax']).toFixed(2)
        picks['done'][categ]['edizioni'] = parseFloat(picks['done'][categ]['edizioni']).toFixed(2)
      });
      this.total_price = total_price.toFixed(2);
      this.price_tax = price_tax.toFixed(2);
      this.edizioni = edizioni.toFixed(2);

      total_price = 0
      price_tax = 0
      edizioni = 0
      $(pickings.refund).each(function (index, value) {
        total_price = total_price + parseFloat(value.total_price);
        price_tax = price_tax + parseFloat(value.price_tax);
        edizioni = edizioni + parseFloat(value.edizioni);
        var categ = value.categ;
        if (categ in picks['refund']) {
          picks['refund'][categ]['qty'] = picks['refund'][categ]['qty'] + parseInt(value.qty)
          picks['refund'][categ]['total_price'] = parseFloat(picks['refund'][categ]['total_price']) + parseFloat(value.total_price)
          picks['refund'][categ]['price_tax'] = parseFloat(picks['refund'][categ]['price_tax']) + parseFloat(value.price_tax)
          picks['refund'][categ]['edizioni'] = parseFloat(picks['refund'][categ]['edizioni']) + parseFloat(value.edizioni)
          picks['refund'][categ]['order'].push(value.sale_id)
        } else {
          picks['refund'][categ] = {
            'qty': parseInt(value.qty),
            'total_price': parseFloat(value.total_price),
            'price_tax': parseFloat(value.price_tax),
            'edizioni': parseFloat(value.edizioni),
            'order': [value.sale_id]
          }
        }
        picks['refund'][categ]['order'] = $.unique(picks['refund'][categ]['order']);
        picks['refund'][categ]['qty_order'] = picks['refund'][categ]['order'].length
        picks['refund'][categ]['total_price'] = parseFloat(picks['refund'][categ]['total_price']).toFixed(2)
        picks['refund'][categ]['price_tax'] = parseFloat(picks['refund'][categ]['price_tax']).toFixed(2)
        picks['refund'][categ]['edizioni'] = parseFloat(picks['refund'][categ]['edizioni']).toFixed(2)


      });
      this.refund_total_price = total_price.toFixed(2);
      this.refund_price_tax = price_tax.toFixed(2);
      this.refund_edizioni = edizioni.toFixed(2);

    }
  })

  var days = Widget.extend({
    template: 'table_vatregister_days',
    init: function (parent, pickings) {
      this.pickings = { 'done': {}, 'refund': {} }
      var total_price = 0;
      var price_tax = 0;
      var edizioni = 0;
      var picks = this.pickings;
      $(pickings.done).each(function (index, value) {
        total_price = total_price + parseFloat(value.total_price);
        price_tax = price_tax + parseFloat(value.price_tax);
        edizioni = edizioni + parseFloat(value.edizioni);
        var day = parseInt(parseDate(value.date_done))
        if (day in picks['done']) {
          picks['done'][day]['qty'] = picks['done'][day]['qty'] + parseInt(value.qty)
          picks['done'][day]['total_price'] = parseFloat(picks['done'][day]['total_price']) + parseFloat(value.total_price)
          picks['done'][day]['price_tax'] = parseFloat(picks['done'][day]['price_tax']) + parseFloat(value.price_tax)
          picks['done'][day]['edizioni'] = parseFloat(picks['done'][day]['edizioni']) + parseFloat(value.edizioni)
          picks['done'][day]['order'].push(value.sale_id)
        } else {
          picks['done'][day] = {
            'qty': parseInt(value.qty),
            'total_price': parseFloat(value.total_price),
            'price_tax': parseFloat(value.price_tax),
            'edizioni': parseFloat(value.edizioni),
            'order': [value.sale_id]
          }
        }
        picks['done'][day]['order'] = $.unique(picks['done'][day]['order']);
        picks['done'][day]['qty_order'] = picks['done'][day]['order'].length
        picks['done'][day]['total_price'] = parseFloat(picks['done'][day]['total_price']).toFixed(2)
        picks['done'][day]['price_tax'] = parseFloat(picks['done'][day]['price_tax']).toFixed(2)
        picks['done'][day]['edizioni'] = parseFloat(picks['done'][day]['edizioni']).toFixed(2)
      });

      // Sort picks 'done' by day
      picks['done'] = Object.keys(picks['done']).sort().reduce((acc, key) => ({
        ...acc, [key]: picks['done'][key]
      }), {})

      this.total_price = total_price.toFixed(2);
      this.price_tax = price_tax.toFixed(2);
      this.edizioni = edizioni.toFixed(2);

      total_price = 0
      price_tax = 0
      edizioni = 0

      $(pickings.refund).each(function (index, value) {
        total_price = total_price + parseFloat(value.total_price);
        price_tax = price_tax + parseFloat(value.price_tax);
        edizioni = edizioni + parseFloat(value.edizioni);
        var day = parseInt(parseDate(value.date_done))
        if (day in picks['refund']) {
          picks['refund'][day]['qty'] = picks['refund'][day]['qty'] + parseInt(value.qty)
          picks['refund'][day]['total_price'] = parseFloat(picks['refund'][day]['total_price']) + parseFloat(value.total_price)
          picks['refund'][day]['price_tax'] = parseFloat(picks['refund'][day]['price_tax']) + parseFloat(value.price_tax)
          picks['refund'][day]['edizioni'] = parseFloat(picks['refund'][day]['edizioni']) + parseFloat(value.edizioni)
          picks['refund'][day]['order'].push(value.sale_id)
        } else {
          picks['refund'][day] = {
            'qty': parseInt(value.qty),
            'total_price': parseFloat(value.total_price),
            'price_tax': parseFloat(value.price_tax),
            'edizioni': parseFloat(value.edizioni),
            'order': [value.sale_id]
          }
        }
        picks['refund'][day]['order'] = $.unique(picks['refund'][day]['order']);
        picks['refund'][day]['qty_order'] = picks['refund'][day]['order'].length
        picks['refund'][day]['total_price'] = parseFloat(picks['refund'][day]['total_price']).toFixed(2)
        picks['refund'][day]['price_tax'] = parseFloat(picks['refund'][day]['price_tax']).toFixed(2)
        picks['refund'][day]['edizioni'] = parseFloat(picks['refund'][day]['edizioni']).toFixed(2)
      });

      // Sort picks 'refund' by day
      picks['refund'] = Object.keys(picks['refund']).sort().reduce((acc, key) => ({
        ...acc, [key]: picks['refund'][key]
      }), {})

      this.refund_total_price = total_price.toFixed(2);
      this.refund_price_tax = price_tax.toFixed(2);
      this.refund_edizioni = edizioni.toFixed(2);

    }

  });

  var multiplayer = Widget.extend({
    template: 'table_vatregister_products',
    init: function (parent, pickings) {
      this.pickings = { 'done': {}, 'refund': {} }
      this.total_price = 0;
      this.price_tax = 0;
      this.edizioni = 0;
      var total_price = this.total_price;
      var price_tax = this.price_tax;
      var edizioni = this.edizioni;
      var picks = this.pickings;


      $(pickings.done).each(function (index, value) {
        if (parseFloat(value.edizioni) > 0) {
          total_price = total_price + parseFloat(value.total_price);
          price_tax = price_tax + parseFloat(value.price_tax);
          edizioni = edizioni + parseFloat(value.edizioni);
          if (value.pid in picks['done']) {
            picks['done'][value.pid]['qty'] = picks['done'][value.pid]['qty'] + parseInt(value.qty)
            picks['done'][value.pid]['total_price'] = parseFloat(picks['done'][value.pid]['total_price']) + parseFloat(value.total_price)
            picks['done'][value.pid]['price_tax'] = parseFloat(picks['done'][value.pid]['price_tax']) + parseFloat(value.price_tax)
            picks['done'][value.pid]['edizioni'] = parseFloat(picks['done'][value.pid]['edizioni']) + parseFloat(value.edizioni)
            picks['done'][value.pid]['order'].push(value.sale_id)
          } else {
            picks['done'][value.pid] = {
              'qty': parseInt(value.qty),
              'product_name': value.product_id,
              'total_price': parseFloat(value.total_price),
              'price_tax': parseFloat(value.price_tax),
              'tax_id': value.tax_id,
              'edizioni': parseFloat(value.edizioni),
              'order': [value.sale_id],
              'barcode': value.barcode
            }
          }
          picks['done'][value.pid]['order'] = $.unique(picks['done'][value.pid]['order']);
          picks['done'][value.pid]['qty_order'] = picks['done'][value.pid]['order'].length

          picks['done'][value.pid]['total_price'] = parseFloat(picks['done'][value.pid]['total_price']).toFixed(2)
          picks['done'][value.pid]['price_tax'] = parseFloat(picks['done'][value.pid]['price_tax']).toFixed(2)
          picks['done'][value.pid]['edizioni'] = parseFloat(picks['done'][value.pid]['edizioni']).toFixed(2)
        }

      })
      this.total_price = total_price.toFixed(2);
      this.price_tax = price_tax.toFixed(2);
      this.edizioni = edizioni.toFixed(2);


      var refund_total_price = 0;
      var refund_price_tax = 0;
      var refund_edizioni = 0;
      var refund_order = [];
      $(pickings.refund).each(function (index, value) {
        if (parseFloat(value.edizioni) > 0) {
          refund_order.push(value.sale_id);
          refund_total_price = refund_total_price + parseFloat(value.total_price);
          refund_price_tax = refund_price_tax + parseFloat(value.price_tax);
          refund_edizioni = refund_edizioni + parseFloat(value.edizioni);
          if (value.pid in picks['refund']) {
            picks['refund'][value.pid]['qty'] = picks['refund'][value.pid]['qty'] + parseInt(value.qty)
            picks['refund'][value.pid]['total_price'] = parseFloat(picks['refund'][value.pid]['total_price']) + value.total_price
            picks['refund'][value.pid]['price_tax'] = parseFloat(picks['refund'][value.pid]['price_tax']) + value.price_tax
            picks['refund'][value.pid]['edizioni'] = parseFloat(picks['refund'][value.pid]['edizioni']) + value.edizioni
            picks['refund'][value.pid]['order'].push(value.sale_id)
          } else {
            picks['refund'][value.pid] = {
              'qty': parseInt(value.qty),
              'product_name': value.product_id,
              'total_price': parseFloat(value.total_price),
              'price_tax': parseFloat(value.price_tax),
              'tax_id': value.tax_id,
              'edizioni': parseFloat(value.edizioni),
              'order': [value.sale_id],
              'barcode': value.barcode
            }
          }
          picks['refund'][value.pid]['order'] = $.unique(picks['refund'][value.pid]['order']);
          picks['refund'][value.pid]['qty_order'] = picks['refund'][value.pid]['order'].length
          picks['refund'][value.pid]['total_price'] = parseFloat(picks['refund'][value.pid]['total_price']).toFixed(2)
          picks['refund'][value.pid]['price_tax'] = parseFloat(picks['refund'][value.pid]['price_tax']).toFixed(2)
          picks['refund'][value.pid]['edizioni'] = parseFloat(picks['refund'][value.pid]['edizioni']).toFixed(2)
        }

      })


      this.refund_total_price = refund_total_price.toFixed(2);
      this.refund_price_tax = refund_price_tax.toFixed(2);
      this.refund_edizioni = refund_edizioni.toFixed(2);

      this.pickings = picks;
    }
  });

  var products = Widget.extend({
    template: 'table_vatregister_products',
    init: function (parent, pickings) {
      this.pickings = { 'done': {}, 'refund': {} }
      this.total_price = 0;
      this.price_tax = 0;
      this.edizioni = 0;
      var total_price = this.total_price;
      var price_tax = this.price_tax;
      var edizioni = this.edizioni;
      var picks = this.pickings;


      $(pickings.done).each(function (index, value) {
        total_price = total_price + parseFloat(value.total_price);
        price_tax = price_tax + parseFloat(value.price_tax);
        edizioni = edizioni + parseFloat(value.edizioni);
        if (value.pid in picks['done']) {
          picks['done'][value.pid]['qty'] = picks['done'][value.pid]['qty'] + parseInt(value.qty)
          picks['done'][value.pid]['total_price'] = parseFloat(picks['done'][value.pid]['total_price']) + parseFloat(value.total_price)
          picks['done'][value.pid]['price_tax'] = parseFloat(picks['done'][value.pid]['price_tax']) + parseFloat(value.price_tax)
          picks['done'][value.pid]['edizioni'] = parseFloat(picks['done'][value.pid]['edizioni']) + parseFloat(value.edizioni)
          picks['done'][value.pid]['order'].push(value.sale_id)
        } else {
          picks['done'][value.pid] = {
            'qty': parseInt(value.qty),
            'product_name': value.product_id,
            'total_price': parseFloat(value.total_price),
            'price_tax': parseFloat(value.price_tax),
            'tax_id': value.tax_id,
            'edizioni': parseFloat(value.edizioni),
            'order': [value.sale_id],
            'barcode': value.barcode
          }
        }
        picks['done'][value.pid]['order'] = $.unique(picks['done'][value.pid]['order']);
        picks['done'][value.pid]['qty_order'] = picks['done'][value.pid]['order'].length
        picks['done'][value.pid]['total_price'] = parseFloat(picks['done'][value.pid]['total_price']).toFixed(2)
        picks['done'][value.pid]['price_tax'] = parseFloat(picks['done'][value.pid]['price_tax']).toFixed(2)
        picks['done'][value.pid]['edizioni'] = parseFloat(picks['done'][value.pid]['edizioni']).toFixed(2)
      })
      this.total_price = total_price.toFixed(2);
      this.price_tax = price_tax.toFixed(2);
      this.edizioni = edizioni.toFixed(2);


      var refund_total_price = 0;
      var refund_price_tax = 0;
      var refund_edizioni = 0;
      var refund_order = [];
      $(pickings.refund).each(function (index, value) {
        refund_order.push(value.sale_id);
        refund_total_price = refund_total_price + parseFloat(value.total_price);
        refund_price_tax = refund_price_tax + parseFloat(value.price_tax);
        refund_edizioni = refund_edizioni + parseFloat(value.edizioni);
        if (value.pid in picks['refund']) {
          picks['refund'][value.pid]['qty'] = picks['refund'][value.pid]['qty'] + parseInt(value.qty)
          picks['refund'][value.pid]['total_price'] = parseFloat(picks['refund'][value.pid]['total_price']) + value.total_price
          picks['refund'][value.pid]['price_tax'] = parseFloat(picks['refund'][value.pid]['price_tax']) + value.price_tax
          picks['refund'][value.pid]['edizioni'] = parseFloat(picks['refund'][value.pid]['edizioni']) + value.edizioni
          picks['refund'][value.pid]['order'].push(value.sale_id)
        } else {
          picks['refund'][value.pid] = {
            'qty': parseInt(value.qty),
            'product_name': value.product_id,
            'total_price': parseFloat(value.total_price),
            'price_tax': parseFloat(value.price_tax),
            'tax_id': value.tax_id,
            'edizioni': parseFloat(value.edizioni),
            'order': [value.sale_id],
            'barcode': value.barcode
          }
        }
        picks['refund'][value.pid]['order'] = $.unique(picks['refund'][value.pid]['order']);
        picks['refund'][value.pid]['qty_order'] = picks['refund'][value.pid]['order'].length
        picks['refund'][value.pid]['total_price'] = parseFloat(picks['refund'][value.pid]['total_price']).toFixed(2)
        picks['refund'][value.pid]['price_tax'] = parseFloat(picks['refund'][value.pid]['price_tax']).toFixed(2)
        picks['refund'][value.pid]['edizioni'] = parseFloat(picks['refund'][value.pid]['edizioni']).toFixed(2)
      })


      this.refund_total_price = refund_total_price.toFixed(2);
      this.refund_price_tax = refund_price_tax.toFixed(2);
      this.refund_edizioni = refund_edizioni.toFixed(2);

      this.pickings = picks;
    }
  });

  core.action_registry.add("netaddiction_receipt_register.receiptdetail", receiptDetail);
  return receiptDetail
})