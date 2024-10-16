# Overview
一个虚拟数字人项目，目标是做起一个虚拟人超市，大家可以在上面通过自行配置虚拟人的人设、人物模型、表情、动作、语音等等，来创建自己想要的虚拟人。
我的一个目标是不断的给我的虚拟人喂数据，然后希望她可以越来越懂我，然后当某一天我想咨询他人的意见的时候，可以问问她，看看她会怎么回答，她的意见是什么样了，会不会有一天她会比我自己更懂我？

特别说明一下：
\- 小白练手：在这个项目之前本人从未接触过typescript, nodejs, django等等，python也是刚刚开始学，更别说是在这些语言和技术下面的海量的第3方组件，一切都是现学现用，若有发现什么问题，请各位大佬不吝赐教！[抱拳][抱拳][抱拳]
\- 一年成本99元：别的虚拟数字人都对硬件要求都特别高，又要GPU，又要高内存，咱也买不起啊，咱只能买阿里云的99块钱一年的VPS，主打一个全民可用（LLM用的第3方的）。

# Features
\- 支持在Linux/Windows/MacOS系统进行部署
\- 支持自定义角色设定
\- 支持更换角色模型，可从VRM模型市场[Vroid](https://hub.vroid.com/)下载
\- 支持长短期记忆功能
\- 支持多LLM模型切换，并且支持私有化模型，具体使用说明请查阅[FAQ](docs/FAQ.md)
\- 支持文字驱动表情，文字驱动动作
\- 支持通过中文进行语音对话
\- 支持Edge（微软）、Bert-VITS2语音切换
\- 流式传输数据，拥有更快的响应速度

# FAQ
\- 项目答疑以及部署中遇到问题的解决方案，请查阅[FAQ](docs/FAQ.md)
\- 本地开发和源码部署请查阅[develop](docs/develop.md)

# 🎉 Roadmap
This platform is currently in beta, a full list of completed and planed features can be found on our public roadmap.
- 后端：[backend develop](docs/SCHEDULE-background.md)
- 前端：[frontend develop](docs/SCHEDULE-foreground.md)

# Get Started
## Clone code

```shell
git clone https://github.com/jackyhwei/xiaoluo
cd xiaoluo
```

## backend
- 进入backend
```shell
cd backend
```

- 创建虚拟环境
```shell
conda create -n vstore python==3.10.12
conda activate vstore
```

- 安装backend项目依赖
```shell
pip3 install -r requirements.txt 
```
代码迭代过程中，依赖项可能会变更，且未及时同步到requirements.txt，若有发现缺失项，请手动安装一下。

- 初始化项目数据库
```shell
python manage.py makemigrations 
```
```shell
python manage.py migrate 
```
- 启动backend项目
```shell
python manage.py runserver
```
- web访问路径
```shell
http://localhost:8000/omserver/
```

## frontend
- 进入frontend文件夹
```shell
cd frontend
```

- 在vstore的虚拟环境下安装node
```shell
conda install -c conda-forge nodejs=15.14.0
```

- 安装frontend项目依赖
```shell
rm package-lock.json
npm install --legacy-peer-deps
```

- 启动frontend项目
```shell
npm run dev
```
- Web访问路径
```shell
http://localhost:3000/
```

- 页面展示

![](docs/16925232398938.jpg)

## 初始化虚拟人配置
### （1）基础配置
```
选择自己喜欢的角色和人物模型，并且选择大语言模型
如果是使用openai请将语言模型设置为openai
```
![](docs/16925233912142.jpg)

### （2）大语言模型配置
```
这以openai模型为例，你只需要将OPENAI_API_KEY填写好即可
如果有API代理可以将地址填写到OPENAI_BASE_URL
```

![](docs/16925238212736.jpg)


如果出现异常请查阅[FAQ](docs/FAQ.md)

# 致谢
本项目部分代码借鉴或直接使用了以下几个开源项目，特别感谢！
- ChatVRM： https://pixiv.github.io/ChatVRM
- Fay: https://github.com/TheRamU/fay
- VirtualWife： https://github.com/yakami129/VirtualWife

# LICENSE
依据 MIT 协议，使用者需自行承担使用本项目的风险与责任，本开源项目开发者与此无关。这个项目采用 GNU通用公共许可证（GPL） 进行许可。有关详细信息，请参阅 LICENSE 文件。

# 💝 Our GitHub sponsors 💝
Join us in fueling the development of Xiaoluo, an open-source project pushing the boundaries of AI agents! Your sponsorship would drive progress by helping us scale up resources, enhance features and functionality, and continue to iterate on this exciting project! 🚀

# 💪 Contributors 💪
Our contributors have made this project possible. Thank you! 🙏

# 注意
严禁将此项目用于一切违反《中华人民共和国宪法》，《中华人民共和国刑法》，《中华人民共和国治安管理处罚法》和《中华人民共和国民法典》之用途。
严禁用于任何政治相关用途。