from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product

@registry.register_document
class ProductDocument(Document):
    """Elasticsearch Document for Product model"""

    # 映射字段
    id = fields.IntegerField()
    name = fields.TextField(
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    goods_brief = fields.TextField()
    category = fields.ObjectField(
        properties={
            'id': fields.IntegerField(),
            'name': fields.KeywordField(),
        }
    )
    shop_price = fields.FloatField()
    sold_num = fields.IntegerField()
    goods_num = fields.IntegerField()
    market_price = fields.FloatField()
    goods_sn = fields.KeywordField()
    is_new = fields.BooleanField()
    is_hot = fields.BooleanField()
    goods_front_image = fields.KeywordField()
    add_time = fields.DateField()

    class Index:
        # 索引名称
        name = 'products'
        # 分片和副本设置（适合开发环境）
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Product
        # 关联的Django模型
        fields = [
            'is_delete',
        ]
        # 自动同步信号（保存/删除时同步更新ES索引）
        related_models = []

        def get_queryset(self):
            # 只索引未逻辑删除的商品
            return super().get_queryset().filter(is_delete=False)

        def get_instances_from_related(self, related_instance):
            # 如果有关联模型需要同步，在此定义
            return None