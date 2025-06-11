import { request } from '@/utils/request.js'

export default {
  /**
   * 获取数据列表
   * @returns
   */
  getPageList(params = {}) {
    return request({
      url: '/app/saicode/table/index',
      method: 'get',
      params
    })
  },

  /**
   * 从回收站获取数据列表
   * @returns
   */
  getRecyclePageList(params = {}) {
    return request({
      url: '/app/saicode/table/recycle',
      method: 'get',
      params
    })
  },

  /**
   * 移到回收站
   * @returns
   */
  deletes(data) {
    return request({
      url: '/app/saicode/table/destroy',
      method: 'delete',
      data
    })
  },

  /**
   * 恢复数据
   * @returns
   */
  recoverys(data) {
    return request({
      url: '/app/saicode/table/recovery',
      method: 'post',
      data
    })
  },

  /**
   * 真实删除数据
   * @returns
   */
  realDestroy(data) {
    return request({
      url: '/app/saicode/table/realDestroy',
      method: 'delete',
      data
    })
  },

  /**
   * 编辑生成信息
   * @returns
   */
  update(id, data = {}) {
    return request({
      url: '/app/saicode/table/update?id=' + id,
      method: 'put',
      data
    })
  },

  /**
   * 读取信息
   * @returns
   */
  readTable(id) {
    return request({
      url: '/app/saicode/table/read?id=' + id,
      method: 'get'
    })
  },

  /**
   * 生成代码
   * @returns
   */
  generateCode(data = {}) {
    return request({
      url: '/app/saicode/table/generate',
      method: 'post',
      responseType: 'blob',
      timeout: 20 * 1000,
      data
    })
  },

  /**
   * 生成到文件
   * @returns
   */
  generateFile(data = {}) {
    return request({
      url: '/app/saicode/table/generateFile',
      method: 'post',
      data
    })
  },

  /**
   * 装载数据表
   * @returns
   */
  loadTable(data = {}) {
    return request({
      url: '/app/saicode/table/loadTable',
      method: 'post',
      data
    })
  },

  /**
   * 同步数据表
   * @returns
   */
  sync(id) {
    return request({
      url: '/app/saicode/table/sync?id=' + id,
      method: 'post'
    })
  },

  /**
   * 预览代码
   * @returns
   */
  preview(id) {
    return request({
      url: '/app/saicode/table/preview?id=' + id,
      method: 'get'
    })
  },

  // 获取表中字段信息
  getTableColumns(params = {}) {
    return request({
      url: '/app/saicode/table/getTableColumns',
      method: 'get',
      params
    })
  },

  // 获取数据源列表
  getDataSource(params = {}) {
    return request({
      url: '/app/saicode/table/source',
      method: 'get',
      params
    })
  },

  // 数据源数据表列表
  getSourceTable(params = {}) {
    return request({
      url: '/app/saicode/table/sourceTable',
      method: 'get',
      params
    })
  },

  // 保存表单设计
  saveDesign(data = {}) {
    return request({
      url: '/app/saicode/table/saveDesign',
      method: 'post',
      data
    })
  }
}
