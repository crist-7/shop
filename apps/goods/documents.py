from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product

# ============================================================
# 中文分词分析器配置
# 使用 IK 分词器：ik_max_word (索引时) + ik_smart (搜索时)
# 前提：Elasticsearch 需安装 elasticsearch-analysis-ik 插件
# ============================================================
IK_INDEX_ANALYZER = 'ik_max_word'   # 索引时：最大化分词，提高召回率
IK_SEARCH_ANALYZER = 'ik_smart'     # 搜索时：智能分词，提高精准度


@registry.register_document
class ProductDocument(Document):
    """
    Elasticsearch Document for Product model
    支持中文分词搜索
    """

    # 映射字段
    id = fields.IntegerField()
    name = fields.TextField(
        analyzer=IK_INDEX_ANALYZER,        # 索引时使用 ik_max_word
        search_analyzer=IK_SEARCH_ANALYZER, # 搜索时使用 ik_smart
        fields={
            'raw': fields.KeywordField(),   # 精确匹配
            'suggest': fields.CompletionField(
                analyzer=IK_INDEX_ANALYZER,  # 自动补全也使用中文分词
            ),
        }
    )
    goods_brief = fields.TextField(
        analyzer=IK_INDEX_ANALYZER,
        search_analyzer=IK_SEARCH_ANALYZER,
    )
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
            # 全局默认分析器配置（作为备用）
            'analysis': {
                'analyzer': {
                    'ik_max_word': {
                        'type': 'ik_max_word'
                    },
                    'ik_smart': {
                        'type': 'ik_smart'
                    }
                }
            }
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