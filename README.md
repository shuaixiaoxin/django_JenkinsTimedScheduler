    jenkins自带定时构建的缺陷
    1. 只能定义在任务里面， 如果多个任务就比较麻烦
    2. 对于触发时间点不固定、或者多任务触发不友好 
    3. 如果任务只在某个时间点触发，并且只触发一次 这样每次都要手动去任务中删掉或修改计划任务

如果你也有以上问题`django_JenkinsTimedScheduler`可以解决你的需求


搭建步骤：

1. 环境准备
python3.7 django3.2.1 mysql5.7

2. 下载源码
```shell
git clone git@github.com:shuaixiaoxin/django_JenkinsTimedScheduler.git
```

3. 安装第三方包
```shell
pip3 install -r requirements.txt
```

4. setting配置  
4.1 数据库配置  
```shell
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
        'NAME': 'jenkins',                      # 创建的数据库
        'USER': 'root',                         # 数据库用户名
        'PASSWORD': '123456',                   # 数据库密码
        'HOST': '127.0.0.1',                    # 数据库地址
        'PORT': '3306'                          # 数据库端口
    }
}
```
4.2 jenkins URL配置  
```shell
JENKINS_URL = ['http://192.168.0.191:8080/'] # 替换成你自己的url地址
```
4.3 默认菜单配置  
```shell
MENU_ID = [4, 5, 6, 7, 8, 9, 10, 11, 12]  # 菜单Id 表示普通用户初始化拥有的菜单权限 默认即可
```
4.4 存储器配置  
```shell
APSCHEDULER_DB = 'mysql+pymysql://root:123456@127.0.0.1:3306/jenkins' # apscheduler存储配置
```
4.5 线上模式（调试模式下可忽略）  
setting配置默认是开启debug模式（DEBUG = True），线上要改为DEBUG = False操作如下：
```shell
STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, "static")  # DEBUG = False 解开注释
STATICFILES_DIRS = (                              # DEBUG = True 注释这行 
os.path.join(BASE_DIR, 'static'),
)
```
5. 数据库生成与迁移
```shell
python3 manage.py makemigrations
python3 manage.py migrate
```

6. 导入菜单sql
打开menu.sql文件 把里面的sql写入或导入到数据库中

7. 启动
```shell
python3 manage.py runserver
``` 
http://127.0.0.1:8000/  
默认用户名：admin 默认密码：admin


8. jenkins生成token
右上角点击用户名——>设置——>API Token——>添加新token——>生成拷贝保存


9. 系统添加token
左侧菜单找到jenkins设置——>token配置——>添加token即可（所创建的用户一定和jenkins用户对应）

部分效果图：
![image](https://github.com/shuaixiaoxin/django_JenkinsTimedScheduler/assets/50731600/960104b3-a117-4564-b4f4-809fed2574e1)
![image](https://github.com/shuaixiaoxin/django_JenkinsTimedScheduler/assets/50731600/c37bc3d0-8186-4b01-90df-73cb557ab0d9)
![image](https://github.com/shuaixiaoxin/django_JenkinsTimedScheduler/assets/50731600/65b27287-0453-4bc7-bace-b2fe37fd8a5e)
![image](https://github.com/shuaixiaoxin/django_JenkinsTimedScheduler/assets/50731600/5713ac50-0bea-4bff-858f-ecbf5d06094e)
