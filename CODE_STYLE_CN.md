# 代码注释规范

本文档定义了AI小说写作平台的代码注释规范，确保代码的可读性和可维护性。

## 通用原则

1. **注释应该解释"为什么"，而不仅仅是"做什么"**
   - ❌ 不好：`# 循环遍历列表`
   - ✅ 好：`# 按优先级处理待处理的任务，确保高优先级任务先执行`

2. **保持注释与代码同步**
   - 修改代码时必须更新相关注释
   - 过时的注释比没有注释更糟糕

3. **使用中文注释**
   - 所有注释统一使用中文
   - 专业术语可以保留英文（如API、JWT、UUID等）

4. **注释要简洁明了**
   - 避免冗长的注释
   - 使用清晰的语言
   - 适当使用示例

## Python后端注释规范

### 模块级注释

每个Python文件顶部应包含模块说明：

```python
"""
模块名称
简短描述模块的功能和用途
"""
from __future__ import annotations

# 导入语句...
```

示例：
```python
"""
小说管理API路由
提供小说的增删改查(CRUD)接口
"""
from __future__ import annotations
```

### 类注释

类定义应包含类的用途说明：

```python
class ClassName:
    """
    类的简短描述
    
    详细说明类的功能、用途和关键属性
    
    Attributes:
        attr1: 属性1的说明
        attr2: 属性2的说明
    """
```

示例：
```python
class Novel(Base):
    """小说模型 - 存储小说的基本信息"""
    __tablename__ = "novels"
    
    id = Column(String(36), primary_key=True)  # 唯一标识符
    title = Column(String(200), nullable=False)  # 标题（必填）
```

### 函数/方法注释

函数和方法应使用docstring注释：

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    函数的简短描述
    
    详细说明函数的功能和行为
    
    Args:
        param1: 参数1的说明
        param2: 参数2的说明
        
    Returns:
        返回值的说明
        
    Raises:
        ExceptionType: 什么情况下抛出异常
    """
```

示例：
```python
async def generate_content(payload: AIGenerateRequest, db: Session = Depends(get_db)):
    """
    使用AI生成内容
    
    Args:
        payload: AI生成请求数据，包含提示词、上下文类型、模型配置等
        db: 数据库会话（依赖注入）
        
    Returns:
        生成的内容、token使用量和模型信息
        
    Raises:
        404: 小说不存在
        500: AI服务错误或数据库错误
    """
```

### 行内注释

重要的代码行应添加简短的行内注释：

```python
# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL)

# 更新列表中的小说
novels.value[index] = response.data
```

### 配置和常量注释

配置项和常量应说明其用途：

```python
class Settings(BaseSettings):
    """应用配置类 - 从环境变量加载配置"""
    
    DATABASE_URL: str = "sqlite:///./ai_novel.db"  # 数据库连接URL，默认使用SQLite
    OPENAI_API_KEY: str = ""  # OpenAI API密钥
    DEBUG: bool = True  # 调试模式开关
```

## TypeScript/Vue前端注释规范

### 文件级注释

每个TypeScript/Vue文件顶部应包含说明：

```typescript
/**
 * 模块名称
 * 简短描述模块的功能和用途
 */
```

示例：
```typescript
/**
 * 小说状态管理Store
 * 使用Pinia管理小说列表、当前小说和相关操作
 */
import { defineStore } from 'pinia'
```

### 接口和类型注释

接口和类型定义应包含说明：

```typescript
/**
 * 接口名称 - 简短描述
 */
export interface InterfaceName {
  field1: string  // 字段1的说明
  field2: number  // 字段2的说明
}
```

示例：
```typescript
/**
 * 小说接口 - 完整的小说信息
 */
export interface Novel {
  id: string  // 小说唯一标识符
  title: string  // 标题
  status: NovelStatus  // 状态：草稿/进行中/已完成/已发布
}
```

### 函数注释

函数应使用JSDoc风格注释：

```typescript
/**
 * 函数的简短描述
 * 
 * @param param1 参数1的说明
 * @param param2 参数2的说明
 * @returns 返回值的说明
 */
function functionName(param1: Type1, param2: Type2): ReturnType {
  // 实现
}
```

示例：
```typescript
/**
 * 使用AI生成内容
 * @param request AI生成请求参数
 * @returns 生成的内容文本
 */
async function generateContent(request: AIRequest) {
  // 实现
}
```

### Vue组件注释

Vue单文件组件应包含组件说明：

```vue
<!--
  组件名称
  功能：组件的主要功能描述
-->
<template>
  <!-- 模板内容 -->
</template>

<script setup lang="ts">
// 脚本内容
</script>
```

示例：
```vue
<!--
  小说列表页面
  功能：展示所有小说、创建新小说、编辑和删除小说
-->
<template>
  <div class="novel-list">
    <!-- ... -->
  </div>
</template>

<script setup lang="ts">
// 路由实例
const router = useRouter()
// 小说Store实例
const novelStore = useNovelStore()
</script>
```

### 变量注释

重要的变量声明应添加注释：

```typescript
// 状态变量
const loading = ref(false)  // 加载状态
const error = ref<string | null>(null)  // 错误信息

// 计算属性
const novelCount = computed(() => novels.value.length)  // 小说总数
```

## 特殊注释标记

使用标准标记来标识特定类型的注释：

- `TODO`: 待实现的功能
  ```python
  # TODO: 实现角色管理功能
  ```

- `FIXME`: 需要修复的问题
  ```python
  # FIXME: 处理并发更新时的冲突
  ```

- `NOTE`: 重要说明
  ```python
  # NOTE: 此处使用缓存以提高性能
  ```

- `WARNING` 或 `WARN`: 警告信息
  ```python
  # WARNING: 不要在生产环境中使用此配置
  ```

- `HACK`: 临时解决方案
  ```python
  # HACK: 临时方案，等待上游库修复
  ```

## 文档注释示例

### 后端API路由完整示例

```python
"""
小说管理API路由
提供小说的增删改查(CRUD)接口
"""
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.novel import Novel
from ..schemas.novel import NovelCreate, NovelResponse, NovelUpdate

# 创建小说路由器，前缀为/api/novels
router = APIRouter(prefix="/api/novels", tags=["novels"])


@router.get("/", response_model=List[NovelResponse])
async def list_novels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    获取小说列表（分页）
    
    Args:
        skip: 跳过的记录数（用于分页）
        limit: 返回的最大记录数
        db: 数据库会话（依赖注入）
        
    Returns:
        小说列表
    """
    novels = db.query(Novel).offset(skip).limit(limit).all()
    return novels
```

### 前端Store完整示例

```typescript
/**
 * 小说状态管理Store
 * 使用Pinia管理小说列表、当前小说和相关操作
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import axios from 'axios'
import type { Novel, NovelCreate } from '@/types/novel'

export const useNovelStore = defineStore('novel', () => {
  // 状态变量
  const novels = ref<Novel[]>([])  // 小说列表
  const loading = ref(false)  // 加载状态
  
  // 计算属性
  const novelCount = computed(() => novels.value.length)  // 小说总数

  /**
   * 获取小说列表
   */
  async function fetchNovels() {
    loading.value = true
    try {
      const response = await axios.get<Novel[]>('/api/novels')
      novels.value = response.data
    } finally {
      loading.value = false
    }
  }

  return {
    novels,
    loading,
    novelCount,
    fetchNovels
  }
})
```

## 注释检查清单

在提交代码前，请确保：

- [ ] 所有新增的模块都有模块级注释
- [ ] 所有公开的类都有类级注释
- [ ] 所有公开的函数/方法都有完整的docstring
- [ ] 复杂的逻辑有行内注释说明
- [ ] 所有接口和类型定义都有注释
- [ ] 注释语言统一使用中文
- [ ] 注释与代码保持同步
- [ ] 没有过时或误导性的注释

## 工具推荐

### Python
- **pylint**: 代码质量检查
- **mypy**: 类型检查
- **pydocstyle**: 文档字符串风格检查

### TypeScript/Vue
- **ESLint**: 代码质量检查
- **TSDoc**: TypeScript文档注释
- **Prettier**: 代码格式化

## 参考资源

- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Vue.js Style Guide](https://vuejs.org/style-guide/)
- [JSDoc Documentation](https://jsdoc.app/)

---

遵循这些注释规范，可以确保代码库的可维护性和团队协作效率。
