{
    "name": "Furniture Manufacturing",
    "version": "19.0.1.0",
    "depends": ["base","product","purchase","sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/furniture_manufacturing_views.xml",
        "views/raw_material_stock_sequence.xml",
        "views/raw_material_stock_views.xml",
        "views/product_template_views.xml",
        "views/finished_goods_views.xml",
        "views/purchase_and_sale_views_inherit.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'furniture_manufacturing/static/src/scss/wood_stock_list.scss',
        ],
    },
    "installable": True,
}