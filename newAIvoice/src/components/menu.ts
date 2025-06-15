import { Menus } from '@/types/menu';
import { ref, computed } from 'vue';

// 基础菜单项
const baseMenuItems: Menus[] = [
  {
    id: '0',
    title: '系统首页',
    index: '/dashboard',
    icon: 'Odometer',
  },
  {
    id: '1',
    title: '后处理任务',
    index: '/task-management',
    icon: 'AlarmClock',
  },
  // {
  //   id: '2',
  //   title: '实时处理任务',
  //   index: '/test',
  //   icon: 'PieChart',
  // },
  //   {
  //     id: '3',
  //     title: '文件处理',
  //     index: '/dashboard',
  //     icon: 'Odometer',
  // },

  //   {
  //     id: '4',
  //     title: '文件降噪',
  //     index: '/dashboard',
  //     icon: 'Odometer',
  // },
  //   {
  //     id: '5',
  //     title: '用户管理',
  //     index: '/dashboard',
  //     icon: 'Odometer',
  // },
  // {
  //     id: '2',
  //     title: '组件',
  //     index: '2-1',
  //     icon: 'Calendar',
  //     children: [
  //         {
  //             id: '21',
  //             pid: '3',
  //             index: '/form',
  //             title: '表单',
  //         },
  //         {
  //             id: '22',
  //             pid: '3',
  //             index: '/upload',
  //             title: '上传',
  //         },
  //         {
  //             id: '23',
  //             pid: '2',
  //             index: '/carousel',
  //             title: '走马灯',
  //         },
  //         {
  //             id: '24',
  //             pid: '2',
  //             index: '/calendar',
  //             title: '日历',
  //         },
  //         {
  //             id: '25',
  //             pid: '2',
  //             index: '/watermark',
  //             title: '水印',
  //         },
  //         {
  //             id: '26',
  //             pid: '2',
  //             index: '/tour',
  //             title: '分布引导',
  //         },
  //         {
  //             id: '27',
  //             pid: '2',
  //             index: '/steps',
  //             title: '步骤条',
  //         },
  //         {
  //             id: '28',
  //             pid: '2',
  //             index: '/statistic',
  //             title: '统计',
  //         },
  //         {
  //             id: '29',
  //             pid: '3',
  //             index: '29',
  //             title: '三级菜单',
  //             children: [
  //                 {
  //                     id: '291',
  //                     pid: '29',
  //                     index: '/editor',
  //                     title: '富文本编辑器',
  //                 },
  //                 {
  //                     id: '292',
  //                     pid: '29',
  //                     index: '/markdown',
  //                     title: 'markdown编辑器',
  //                 },
  //             ],
  //         },
  //     ],
  // },
  // {
  //     id: '3',
  //     title: '表格',
  //     index: '3',
  //     icon: 'Calendar',
  //     children: [
  //         {
  //             id: '31',
  //             pid: '3',
  //             index: '/table',
  //             title: '基础表格',
  //         },
  //         {
  //             id: '32',
  //             pid: '3',
  //             index: '/table-editor',
  //             title: '可编辑表格',
  //         },
  //         {
  //             id: '33',
  //             pid: '3',
  //             index: '/import',
  //             title: '导入Excel',
  //         },
  //         {
  //             id: '34',
  //             pid: '3',
  //             index: '/export',
  //             title: '导出Excel',
  //         },
  //     ],
  // },
  // {
  //     id: '4',
  //     icon: 'PieChart',
  //     index: '4',
  //     title: '图表',
  //     children: [
  //         {
  //             id: '41',
  //             pid: '4',
  //             index: '/schart',
  //             title: 'schart图表',
  //         },
  //         {
  //             id: '42',
  //             pid: '4',
  //             index: '/echarts',
  //             title: 'echarts图表',
  //         },
  //     ],
  // },
  // {
  //     id: '5',
  //     icon: 'Guide',
  //     index: '/icon',
  //     title: '图标',
  //     permiss: '5',
  // },
  // {
  //     id: '7',
  //     icon: 'Brush',
  //     index: '/theme',
  //     title: '主题',
  // },
  // {
  //     id: '6',
  //     icon: 'DocumentAdd',
  //     index: '6',
  //     title: '附加页面',
  //     children: [
  //         {
  //             id: '61',
  //             pid: '6',
  //             index: '/ucenter',
  //             title: '个人中心',
  //         },
  //         {
  //             id: '62',
  //             pid: '6',
  //             index: '/login',
  //             title: '登录',
  //         },
  //         {
  //             id: '63',
  //             pid: '6',
  //             index: '/register',
  //             title: '注册',
  //         },
  //         {
  //             id: '64',
  //             pid: '6',
  //             index: '/reset-pwd',
  //             title: '重设密码',
  //         },
  //         {
  //             id: '65',
  //             pid: '6',
  //             index: '/403',
  //             title: '403',
  //         },
  //         {
  //             id: '66',
  //             pid: '6',
  //             index: '/404',
  //             title: '404',
  //         },
  //     ],
  // },
];

// 管理员专属菜单项
const adminMenuItems: Menus[] = [
  {
    id: '3',
    title: '管理用户',
    index: '/manage-users',
    icon: 'UserFilled',
  },
  {
    id: '4',
    title: '管理任务',
    index: '/manage-tasks',
    icon: 'ChatLineSquare',
  },
];

// 使用计算属性动态生成菜单
export const getMenuData = () => {
  const userRole = localStorage.getItem('role');
  const isAdmin = userRole === '1';
  
  return [
    ...baseMenuItems,
    ...(isAdmin ? adminMenuItems : []),
  ];
};

// 导出初始菜单数据
export const menuData = getMenuData();
