/**
 * 小说相关的TypeScript类型定义
 */

// 小说状态类型
export type NovelStatus = 'DRAFT' | 'IN_PROGRESS' | 'COMPLETED' | 'PUBLISHED'

/**
 * 小说接口 - 完整的小说信息
 */
export interface Novel {
  id: string  // 小说唯一标识符
  title: string  // 标题
  author?: string | null  // 作者
  genre?: string | null  // 类型/流派
  description?: string | null  // 简介
  status: NovelStatus  // 状态：草稿/进行中/已完成/已发布
  created_at: string  // 创建时间（ISO格式字符串）
  updated_at: string  // 更新时间（ISO格式字符串）
}

/**
 * 小说创建接口 - 用于创建新小说
 */
export interface NovelCreate {
  title: string  // 标题（必填）
  author?: string | null  // 作者（可选）
  genre?: string | null  // 类型（可选）
  description?: string | null  // 简介（可选）
  status?: NovelStatus  // 状态（可选，默认为DRAFT）
}

/**
 * 小说更新接口 - 用于更新现有小说（所有字段可选）
 */
export interface NovelUpdate {
  title?: string  // 标题
  author?: string | null  // 作者
  genre?: string | null  // 类型
  description?: string | null  // 简介
  status?: NovelStatus  // 状态
}
