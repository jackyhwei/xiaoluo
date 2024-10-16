# Overview
小落同学：一个虚拟数字人项目，目标是做一个私人的日记本，将你每天的记忆进行保存，然后等有一天记忆的容量达到一定程度后，可以克隆出来另一个你自己。
不过，早先走过许多弯路，也写了好多代码，一下子舍不得全删了，所以选择性的保留了一些虚拟人超市的功能，大家可以在上面通过自行配置虚拟人的人设、人物模型、表情、动作、语音等等，来创建自己想要的虚拟人。

# 项目目标
\- **小白练手**：在这个项目之前本人从未接触过typescript, nodejs, django等等，python也是刚刚开始学，更别说是在这些语言和技术下面的海量的第3方组件，一切都是现学现用，若有发现什么问题，请各位大佬不吝赐教！[抱拳][抱拳][抱拳]。曾经尝试过加入一些他人的开源项目来进行学习，但是写了好多代码与功能，在递交了pull request后，可能代码风格、代码质量与owner的要求相去甚远，经常长时间无法合入，因此还是考虑自己来搞个项目练手比较合适。
\- **知我懂我**：我的一个目标是不断的给我的虚拟人喂数据，然后希望她可以越来越懂我，然后当某一天我想咨询他人的意见的时候，可以问问她，看看她会怎么回答？她的意见如何？会不会有一天她会比我自己更懂我？会不会有一天真的可以变出来另外一个我自己？

# 部署成本
\- 服务器成本：0元或者99元/年
	- 自备电脑：0元。我猜许多人家里都应该有放着一些N年前的老笔记本、老电脑在吃灰，现在我告诉你，只要是没超过20年的电脑，跑跑“小落同学”都应该是绰绰有余的。
	- 云服务器：99元/年。别的虚拟数字人都对硬件要求都特别高，又要GPU，又要高内存，咱也买不起啊，咱只能买阿里云的99块钱一年的VPS，主打一个全民智能。[阿里云99元活动](https://www.aliyun.com/daily-act/ecs/99program)截止时间：2026年3月31日。
\- 大语言模型成本：0元。原先用的是一个前同事公司的，现在国内好多免费的大模型可以白嫖，所以，原则上能不多花一分钱的咱就不花。另加上咱们的目的主要还是把这个产品当作一个日记本、一个记忆库来使用，因此也对大语言模型的要求不会非常的高，推荐使用百度的文心一言[ERNIE SPEED](https://console.bce.baidu.com/qianfan/modelcenter/model/buildIn/list)（偶尔有一些问题想问大模型的，ernie speed版本也够对付的了）

# Demo
我自己的demo放在: https://x.rg4.net，我给她取的名字叫：小落同学。
我会每天跟她讲一下今天做了些什么事情，有什么开心的、不开心的、喜欢的、讨厌的人或事，就当是一个日记本来用。

***\*但是\****：
请大家不要在我的demo上去喂你个人的数据，我不想看到你的任何个人数据，乃至隐私信息。
如果你跟我一样的“富有”，花的起一年99块钱的话，建议自己买一个VPS来搭建你自己的私人平台。
但是如果你比我还穷，还抠门，口袋里没有99块钱的话，也可以随便找一个N年前的老电脑来搭这个平台，只要是20年以内的老电脑运行本系统也毫无压力。

# Features
\- 支持在Linux/Windows/MacOS系统进行部署
\- 支持自定义角色人设
\- 支持自定义角色动作、表情
\- 支持更换角色模型，可从VRM模型市场[Vroid](https://hub.vroid.com/)下载
\- 支持长短期记忆功能
\- 支持虚拟人根据近期的记忆自主找话题
\- 支持文字驱动表情，文字驱动动作
\- 支持通过中文进行语音对话
\- 支持Edge（微软）、Bert-VITS2语音切换
\- 流式传输数据，拥有更快的响应速度

# FAQ
\- 项目答疑以及部署中遇到问题的解决方案，请查阅[FAQ](docs/FAQ.md)
\- 本地开发和源码部署请查阅[develop](docs/develop.md)

# 🎉 Roadmap
This platform is currently in beta, a full list of completed and planed features can be found on our public roadmap.
\- 后端：[backend develop](docs/SCHEDULE-background.md)
\- 前端：[frontend develop](docs/SCHEDULE-foreground.md)

# Get Started
开始之前，我假定你有环境已经有安装 git、conda，并且会一点点相关的命令。如果你对这两个工具都是小白的话，建议你先看看网上的一些教程。
相关百度百科：
\- git: https://baike.baidu.com/item/GIT/12647237
\- conda: https://baike.baidu.com/item/anaconda/20407441
安装好git和conda之后就可以往下走了。

**## Clone code**
\```shell
git clone https://github.com/jackyhwei/xiaoluo
cd xiaoluo
\```

**## backend**
\- 进入backend
\```shell
cd backend
\```

\- 创建虚拟环境
\```shell
conda create -n vstore python==3.10.12
conda activate vstore
\```

\- 安装backend项目依赖
\```shell
pip3 install -r requirements.txt 
\```

代码迭代过程中，依赖项可能会变更，且未及时同步到requirements.txt，若有发现缺失项，请手动安装一下。

\- 初始化项目数据库
\```shell
python manage.py makemigrations 
\```

\```shell
python manage.py migrate 
\```

\- 启动backend项目
\```shell
python manage.py runserver
\```

\- web访问路径
\```shell
http://localhost:8000/omserver/
\```

**## frontend**
\- 进入frontend文件夹
\```shell
cd frontend
\```

\- 在vstore的虚拟环境下安装node
\```shell
conda install -c conda-forge nodejs=15.14.0
\```

\- 安装frontend项目依赖
\```shell
rm package-lock.json
npm install --legacy-peer-deps
\```

\- 启动frontend项目
\```shell
npm run dev
\```

\- Web访问路径
\```shell
http://localhost:3000/
\```

\- 页面展示
![](docs/xiaoluo.jpg)

**## 初始化虚拟人配置**

**### （1）基础配置**
\```
选择自己喜欢的角色和人物模型，并且选择大语言模型
如果是使用文心一言请将语言模型设置为文心一言
\```
**### （2）大语言模型配置**
\```
这以文心一言模型为例，你只需要先在[百度控制台](https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application/v1)上创建好应用，并将该应用所对应的APP KEY和SECRET KEY在[管理后台](http://localhost:8000/omserver/llm_settings)给填写好即可。
\```

![](docs/llm-api-key.png)

如果出现异常请查阅[FAQ](docs/FAQ.md)

# 致谢
本项目部分代码借鉴或直接使用了以下几个开源项目，特别感谢！
\- ChatVRM： https://pixiv.github.io/ChatVRM
\- Fay: https://github.com/TheRamU/fay
\- VirtualWife： https://github.com/yakami129/VirtualWife

# LICENSE
依据 MIT 协议，使用者需自行承担使用本项目的风险与责任，本开源项目开发者与此无关。这个项目采用 GNU通用公共许可证（GPL） 进行许可。有关详细信息，请参阅 LICENSE 文件。

# 💝 Our GitHub sponsors 💝
Join us in fueling the development of Xiaoluo, an open-source project pushing the boundaries of AI agents! Your sponsorship would drive progress by helping us scale up resources, enhance features and functionality, and continue to iterate on this exciting project! 🚀

# 💪 Contributors 💪
Our contributors have made this project possible. Thank you! 🙏

# 注意
严禁将此项目用于一切违反《中华人民共和国宪法》，《中华人民共和国刑法》，《中华人民共和国治安管理处罚法》和《中华人民共和国民法典》之用途。
严禁用于任何政治相关用途。
