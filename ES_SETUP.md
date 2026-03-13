# Elasticsearch 搜索功能配置指南

## 1. 启动服务

### 开发环境
```bash
docker-compose -f docker-compose.dev.yml up
```

### 生产环境
```bash
docker-compose up
```

服务启动后，Elasticsearch 将在 http://localhost:9200 可用。

## 2. 创建 Elasticsearch 索引

在 Django 容器内执行以下命令创建索引：

```bash
# 进入后端容器
docker exec -it shop-backend-dev bash

# 创建索引
python manage.py search_index --create

# 查看索引状态
python manage.py search_index --list

# 重建索引（清空并重新导入所有数据）
python manage.py search_index --rebuild
```

或者直接通过 Docker Compose 执行：

```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py search_index --rebuild
```

## 3. 数据同步

### 自动同步
Django 信号已配置，当商品数据在 MySQL 中发生变更时，会自动同步到 Elasticsearch 索引。

### 手动同步
如果需要手动同步所有商品数据：

```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py search_index --populate
```

## 4. 测试搜索功能

### 验证 Elasticsearch 运行
```bash
curl http://localhost:9200/_cat/indices?v
```

应看到名为 `products` 的索引。

### 测试 API 搜索
使用浏览器或 curl 测试搜索接口：

```
GET /api/goods/?search=手机
GET /api/goods/?search=智能&category=1
```

### 前端测试
1. 访问 http://localhost:5173
2. 在搜索框中输入关键词（如"手机"）
3. 查看搜索结果列表

## 5. 故障排除

### Elasticsearch 启动失败
- 检查内存：Elasticsearch 需要至少 512MB 内存
- 检查端口：9200 端口是否被占用
- 查看日志：`docker logs shop-elasticsearch-dev`

### 索引创建失败
- 确保 Elasticsearch 服务已启动且健康
- 检查网络：backend 容器能否访问 elasticsearch:9200
- 验证配置：`ELASTICSEARCH_HOST` 环境变量是否正确

### 搜索无结果
1. 确认索引中存在数据：
   ```bash
   curl -X GET "http://localhost:9200/products/_search?pretty"
   ```
2. 检查数据是否同步：
   ```bash
   curl -X GET "http://localhost:9200/products/_count?pretty"
   ```
3. 重建索引：
   ```bash
   python manage.py search_index --rebuild
   ```

### 性能优化建议
1. **增加内存**：在 docker-compose.yml 中调整 `ES_JAVA_OPTS`
2. **配置 IK 分词器**（如需中文分词）：
   ```Dockerfile
   # 自定义 Dockerfile 安装 IK 插件
   RUN elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.17.23/elasticsearch-analysis-ik-7.17.23.zip
   ```
3. **调整分片设置**：在 `documents.py` 中修改 `number_of_shards` 和 `number_of_replicas`

## 6. 开发注意事项

### 本地开发
本地运行 Django（非 Docker）时，需要设置 `ELASTICSEARCH_HOST` 环境变量：

```bash
export ELASTICSEARCH_HOST=http://localhost:9200
```

或使用 `setup_local.ps1` 脚本。

### 生产部署
1. 为 Elasticsearch 配置持久化存储
2. 设置适当的 JVM 堆大小（建议 1-4GB）
3. 启用安全配置（xpack.security）
4. 配置备份策略

## 7. 扩展功能

### 搜索建议（Autocomplete）
已在 `ProductDocument` 中配置 `suggest` 字段，可通过以下方式实现搜索建议：

```python
# 在 views.py 中添加
suggest_search = ProductDocument.search().suggest(
    'product_suggest',
    search_query,
    completion={'field': 'name.suggest'}
)
```

### 高级搜索特性
可扩展的功能包括：
- 价格区间过滤
- 多级分类筛选
- 搜索结果高亮
- 相关度排序优化
- 搜索词分析统计