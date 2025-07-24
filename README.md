# N1MM Wavelog uploader

N1MM输出的日志和JTDX有些不太“一样”，导致目前已有的工具无法直接正确传递日志，因此我写了一个简单的解析器用来上传N1MM的日志到自建的Wavelog实例上，希望将来其它项目也尽快兼容N1MM。

配置文件说明：
| 配置项              | 值                                 | 说明                                       |
|-------------------|------------------------------------|------------------------------------------|
| `udp_port`        | `2333`                             | UDP监听端口，N1MM Logger会向此端口发送数据    |
| `wavelog_url`     | `https://your-wavelog-url.com`     | Wavelog服务器地址                            |
| `api_key`         | `your-api-key-here`                | Wavelog API密钥                            |
| `station_profile_id` | `1`                            | 台站配置文件ID                              |
| `listen_address`  | `0.0.0.0`                          | 监听地址，0.0.0.0表示监听所有网卡             |


使用效果如下：

- 第一次运行会在运行目录生成配置文件模板，按照自己的Wavelog服务器信息填写即可。
![](https://assets.moedev.cn/blog/photo/images/2025/20250721171828887.png!webp)

- 配置正确后会解析N1MM日志上传到Wavelog
![](https://assets.moedev.cn/blog/photo/images/2025/QQ_1753089828395.png!webp)

![](https://assets.moedev.cn/blog/photo/images/2025/QQ_1753089929123.png!webp)