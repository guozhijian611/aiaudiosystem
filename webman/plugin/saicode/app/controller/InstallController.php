<?php
// +----------------------------------------------------------------------
// | saiadmin [ saiadmin快速开发框架 ]
// +----------------------------------------------------------------------
// | Author: sai <1430792918@qq.com>
// +----------------------------------------------------------------------
namespace plugin\saicode\app\controller;

use plugin\saiadmin\exception\ApiException;
use think\facade\Db;
use Throwable;

/**
 * 安装控制器
 */
class InstallController
{
    /**
     * 应用名称
     * @var string
     */
    protected string $app = 'saicode';

    /**
     * 安装执行
     */
    public function index(): string
    {
        // 检验插件是否已经安装
        $path = base_path() . DIRECTORY_SEPARATOR . 'plugin' . DIRECTORY_SEPARATOR . $this->app;
        if (is_file($path. DIRECTORY_SEPARATOR . 'public' . DIRECTORY_SEPARATOR . 'install.lock')) {
            return '<h3 style="color:#ff0000">插件【'.$this->app.'】已经安装，无需重复安装</h3>';
        }
        // 检验插件安装环境
        $config = config('plugin.saiadmin.app');
        if (is_null($config)) {
            return '<h3>在安装saiadmin插件之前，请先安装<a href="https://saithink.top/" target="_blank">【saiadmin】</a></h3>';
        }
        // 执行安装过程
        $this->installSql();
        file_put_contents($path. DIRECTORY_SEPARATOR . 'public' . DIRECTORY_SEPARATOR . 'install.lock', 'ok');
        return '<h3 style="color:#069f5b">插件【'.$this->app.'】安装成功</h3>';
    }

    /**
     * 安装SQL
     * @return void
     */
    protected function installSql(): void
    {
        $path = base_path() . DIRECTORY_SEPARATOR . 'plugin' . DIRECTORY_SEPARATOR . $this->app;
        $sql = $path . DIRECTORY_SEPARATOR . 'db' . DIRECTORY_SEPARATOR . 'install.sql';
        $this->importSql($sql);
    }

    /**
     * 卸载SQL
     * @return void
     */
    protected function uninstallSql() {
        $path = base_path() . DIRECTORY_SEPARATOR . 'plugin' . DIRECTORY_SEPARATOR . $this->app;
        $uninstallSqlFile = $path . DIRECTORY_SEPARATOR . 'db' . DIRECTORY_SEPARATOR . 'uninstall.sql';
        if (is_file($uninstallSqlFile)) {
            static::importSql($uninstallSqlFile);
        }
        throw new ApiException('未找到卸载SQL文件');
    }

    /**
     * 导入数据库
     * @param $mysqlDumpFile
     * @return void
     */
    protected function importSql($mysqlDumpFile): void
    {
        if (!$mysqlDumpFile || !is_file($mysqlDumpFile)) {
            return;
        }
        foreach (explode(';', file_get_contents($mysqlDumpFile)) as $sql) {
            if ($sql = trim($sql)) {
                try {
                    Db::execute($sql);
                } catch (Throwable $e) {
                    throw new ApiException($e->getMessage());
                }
            }
        }
    }

}
