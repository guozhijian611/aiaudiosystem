# 任务列表搜索和排序功能使用说明

## 功能概述

任务列表现在支持以下功能：
- 关键词搜索（任务名称和任务编号）
- 多字段排序
- 状态筛选
- 时间范围筛选
- 分页查询

## API 参数说明

### 后端接口参数

**POST** `/task/tasklist`

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | int | 否 | 1 | 页码 |
| limit | int | 否 | 10 | 每页数量 |
| search | string | 否 | '' | 搜索关键词，支持任务名称和编号搜索 |
| sort | string | 否 | 'id' | 排序字段：id, name, number, status, create_time, update_time |
| order | string | 否 | 'desc' | 排序方向：asc(升序), desc(降序) |
| status | int | 否 | '' | 状态筛选：1-空任务, 2-已检测, 3-已转写, 4-处理中, 5-暂停中 |
| start_time | string | 否 | '' | 开始时间，格式：Y-m-d |
| end_time | string | 否 | '' | 结束时间，格式：Y-m-d |

### 返回数据结构

```json
{
  "code": 200,
  "msg": "获取任务列表成功",
  "data": {
    "list": [...],
    "total": 100,
    "current_page": 1,
    "per_page": 10,
    "last_page": 10,
    "has_more": true,
    "search_info": {
      "search": "关键词",
      "sort": "create_time",
      "order": "desc",
      "status": 1,
      "start_time": "2024-01-01",
      "end_time": "2024-12-31"
    },
    "status_options": [
      {"value": 1, "label": "空任务"},
      {"value": 2, "label": "已检测"},
      {"value": 3, "label": "已转写"},
      {"value": 4, "label": "处理中"},
      {"value": 5, "label": "暂停中"}
    ],
    "sort_options": [
      {"value": "id", "label": "ID"},
      {"value": "name", "label": "任务名称"},
      {"value": "number", "label": "任务编号"},
      {"value": "status", "label": "任务状态"},
      {"value": "create_time", "label": "创建时间"},
      {"value": "update_time", "label": "更新时间"}
    ]
  }
}
```

## 前端调用示例

### 方式一：使用完整参数

```javascript
import { getTaskList } from '@/api/task';

// 基础查询
const result = await getTaskList(1, 10);

// 搜索查询
const searchResult = await getTaskList(1, 10, '音频任务');

// 完整查询
const fullResult = await getTaskList(
  1,                    // page
  10,                   // limit
  '音频任务',             // search
  'create_time',        // sort
  'desc',              // order
  4,                   // status (处理中)
  '2024-01-01',        // start_time
  '2024-12-31'         // end_time
);
```

### 方式二：使用对象参数（推荐）

```javascript
import { getTaskListWithOptions } from '@/api/task';

// 基础查询
const result = await getTaskListWithOptions();

// 搜索查询
const searchResult = await getTaskListWithOptions({
  search: '音频任务',
  page: 1,
  limit: 20
});

// 按创建时间排序
const sortedResult = await getTaskListWithOptions({
  sort: 'create_time',
  order: 'desc'
});

// 筛选处理中的任务
const processingTasks = await getTaskListWithOptions({
  status: 4,
  sort: 'update_time',
  order: 'desc'
});

// 查询指定时间范围内的任务
const timeRangeResult = await getTaskListWithOptions({
  start_time: '2024-01-01',
  end_time: '2024-12-31',
  sort: 'create_time',
  order: 'asc'
});

// 复合查询
const complexResult = await getTaskListWithOptions({
  search: '重要',
  status: 3,
  start_time: '2024-01-01',
  end_time: '2024-12-31',
  sort: 'update_time',
  order: 'desc',
  page: 1,
  limit: 15
});
```

## 前端组件使用示例

### Vue.js 示例

```vue
<template>
  <div class="task-list">
    <!-- 搜索和筛选表单 -->
    <div class="search-form">
      <el-input 
        v-model="searchForm.search" 
        placeholder="搜索任务名称或编号"
        @input="handleSearch"
        clearable
      />
      
      <el-select 
        v-model="searchForm.status" 
        placeholder="选择状态"
        @change="handleSearch"
        clearable
      >
        <el-option 
          v-for="option in statusOptions" 
          :key="option.value"
          :label="option.label" 
          :value="option.value"
        />
      </el-select>
      
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change="handleDateChange"
      />
      
      <el-select 
        v-model="searchForm.sort" 
        placeholder="排序字段"
        @change="handleSearch"
      >
        <el-option 
          v-for="option in sortOptions" 
          :key="option.value"
          :label="option.label" 
          :value="option.value"
        />
      </el-select>
      
      <el-select 
        v-model="searchForm.order" 
        @change="handleSearch"
      >
        <el-option label="降序" value="desc" />
        <el-option label="升序" value="asc" />
      </el-select>
    </div>

    <!-- 任务列表 -->
    <el-table :data="taskList" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="number" label="任务编号" />
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" />
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.limit"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { getTaskListWithOptions } from '@/api/task';

// 响应式数据
const loading = ref(false);
const taskList = ref([]);
const dateRange = ref([]);

const searchForm = reactive({
  search: '',
  status: '',
  sort: 'create_time',
  order: 'desc',
  start_time: '',
  end_time: ''
});

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0
});

const statusOptions = ref([]);
const sortOptions = ref([]);

// 方法
const loadTasks = async () => {
  loading.value = true;
  try {
    const response = await getTaskListWithOptions({
      ...searchForm,
      page: pagination.page,
      limit: pagination.limit
    });
    
    if (response.code === 200) {
      taskList.value = response.data.list;
      pagination.total = response.data.total;
      statusOptions.value = response.data.status_options;
      sortOptions.value = response.data.sort_options;
    }
  } catch (error) {
    console.error('加载任务列表失败:', error);
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  pagination.page = 1;
  loadTasks();
};

const handleDateChange = (dates) => {
  if (dates && dates.length === 2) {
    searchForm.start_time = dates[0];
    searchForm.end_time = dates[1];
  } else {
    searchForm.start_time = '';
    searchForm.end_time = '';
  }
  handleSearch();
};

const handleSizeChange = (size) => {
  pagination.limit = size;
  pagination.page = 1;
  loadTasks();
};

const handlePageChange = (page) => {
  pagination.page = page;
  loadTasks();
};

const getStatusLabel = (status) => {
  const option = statusOptions.value.find(item => item.value === status);
  return option ? option.label : '未知';
};

const getStatusType = (status) => {
  const types = {
    1: 'info',    // 空任务
    2: 'warning', // 已检测
    3: 'success', // 已转写
    4: 'primary', // 处理中
    5: 'danger'   // 暂停中
  };
  return types[status] || 'info';
};

// 生命周期
onMounted(() => {
  loadTasks();
});
</script>
```

## 安全说明

1. **SQL注入防护**：排序字段已做白名单验证
2. **参数验证**：所有输入参数都有类型和范围验证
3. **用户权限**：只能查询当前用户的任务
4. **时间格式**：时间参数会自动添加时分秒范围

## 性能优化建议

1. **索引优化**：为常用搜索字段创建数据库索引
   ```sql
   CREATE INDEX idx_task_uid_name ON ai_task(uid, name);
   CREATE INDEX idx_task_uid_number ON ai_task(uid, number);
   CREATE INDEX idx_task_uid_status ON ai_task(uid, status);
   CREATE INDEX idx_task_uid_create_time ON ai_task(uid, create_time);
   ```

2. **缓存策略**：对于频繁查询的数据可以考虑使用Redis缓存

3. **分页限制**：建议限制最大每页数量，避免大量数据查询

4. **搜索优化**：对于大数据量可以考虑使用全文搜索引擎如Elasticsearch 