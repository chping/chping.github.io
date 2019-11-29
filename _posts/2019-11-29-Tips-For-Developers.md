---
layout:     post
title:      开放常用命令和技巧
subtitle:   开发
date:       2019-11-29
author:     Ping
header-img: img/post-bg-cook.jpg
catalog: true
tags:
    - Coding
    - Development
---

[toc]

# sqlite
## sqlite 导出数据库到csv
```sqlite
$ sqlite3 xxx.db
sqlite> .headers on
sqlite> .mode csv
sqlite> .output data.csv
sqlite> select * from `TableName`;
sqlite> .quit
```
.mode 设置输出模式
* csv 逗号分隔的值
* column 左对齐的列
* html HTML 的 <table> 代码
* insert TABLE 表 SQL 插入语句
* line 每行一个值
* list 由 .separator 字符串分隔的值
* tabs 由 Tab 分隔的值
* tcl TCL 列表元素
导出完毕后输入 .output stdout 就可以恢复正常输出到控制台
## sqlite – 如何将查询的结果保存为CSV文件？
您必须将输出切换到csv模式并切换到文件输出。
sqlite> .mode csv
sqlite> .output test.csv
sqlite> select * from tbl1;
sqlite> .output stdout


# git
## 提交发现冲突时批处理冲突文件

1、进入项目目录，输入下面的命令查找所有冲突文件（注意命令最后面的 . 代表当前目录
```bash
grep -lr '<<<<<<<' .
```
2、处理冲突文件
```bash
# 接受文件本地更改的版本（忽略远程服务器的版本）
git checkout --ours <Conflict Files>

# 接受文件远程更改的版本（忽略本地的版本）
git checkout --theirs <Conflict Files>
```

3、结合前面查找冲突文件的命令，批量处理所有冲突文件

```bash
# 接受所有本地更改的文件版本
grep -lr '<<<<<<<' . | xargs git checkout --ours

# 接受所有远程更高的文件版本
grep -lr '<<<<<<<' . | xargs git checkout --theirs

```

## git 删除之前版本库中的忽略的文件
git rm -r --cached <文件名>

## git 回滚到某个历史commit并强制覆盖远端

首先用下面的命令回滚到某个历史Commit
git reset --hard <commit_ID>
然后强制Push到远端
git push -f -u origin <branch>  

## 清除本地修改
```bash
git reset --hard
```

## 克隆仓库的某个分支（例如dev分支）
```bash
git clone -b dev https://xxx.git
```

## 查看所有分支
```bash
git branch -a
```

## 切换本地仓库到某个分支
```bash
git checkout origin/dev
```

## 配置git仓库自动保存密码
```bash
git config credential.helper store
```

## git checkout $commit_SHA1 回滚到某个commit的历史版本

例如
git checkout 271e8c50ba1acc1002601cc12643dfbdef4c7005
将回滚到这个SHA1所属commit的版本，此时HEAD为Detached HEAD, 无法commit
如果要把回滚的代码重新提交到主分支，需要创建一个临时分支，然后Pull Request Merge到原来的分支，再删除这个临时分支
```bash
$git checkout –b temp #makes a new branch from current detached HEAD
$git branch –f master temp #update master to point to the new <temp> branch
$git checkout master  #Switch to master branch
$git branch –d temp #delete the <temp> branch
$git push -f origin master #push the re-established history
```
## 利用git hook当向本地仓库提交commit后触发构建任务
* 在项目的 .git/hooks  目录下新建 post-commit 文件
* 修改文件内容，例如
```bash
  1 #!/bin/sh   
  2 WORKSPACE=/Users/chengping/Documents/Ping/codes/build
  3 echo ${WORKSPACE}
  4 cd ${WORKSPACE}
  5 `. build.sh`
```

## git 根据commit id创建和删除tag

创建一个Tag: 
```git
git tag -a <tag_name> <commit_id> -m "messages or comments"

# example
git tag -a v2.0.2 07a0d69 -m "Adding tag to published version 2.0.2"
```
Push 到服务器
```git
git push origin <tag_name>

#example
git push origin v2.0.2
```

删除 Tag
```git
git push --delete origin <tag_name>

#example
git push --delete origin v2.0.2

```

# VSCode / C# / Unity / Firebase / Android

## VS code debug on Android throgh react native
You can open developer menu in Emulator or device by
adb shell input keyevent 82

## C#如何用类似枚举的方式来定义类型安全的字符常量
```C#
/// <summary>
/// 事件记录自定义参数名称列表
/// </summary>
public class ParamName {
	public string Value { get; set; }
  private ParamName(string value) { Value = value; }
  public static ParamName COIN_SOURCE_REWARDVIDEO { get { return new ParamName("ByRewardVideo"); } }
  public static ParamName COIN_COIN_SOURCE_PASS_LEVEL { get { return new ParamName("ByPassLevel"); } }
  public static ParamName COIN_SOURCE_PASS_CHAPTER { get { return new ParamName("ByPassChapter"); } }
  public static ParamName COIN_SOURCE_DAILY_SIGNIN { get { return new ParamName("ByDailySignIn"); } }
    }
```
## Firebase 在Android logcat中输出事件记录日志方便调试

您可以在 Android Studio 调试日志中启用详细的日志记录功能，从而帮助验证 SDK 是否已正确记录事件。这包括自动和手动记录的事件。
您可以通过一系列 adb 命令启用详细的日志记录功能：

```bash
adb shell setprop log.tag.FA VERBOSE
adb shell setprop log.tag.FA-SVC VERBOSE
adb logcat -v time -s FA FA-SVC
```

此命令可在 Android Studio logcat 中显示您的事件，帮助您立即验证所发送的事件。

## Firebase 在Android和iOS设备上启用“调试模式”以便看到即时的调试数据

Android
要在 Android 模拟设备上启用 Analytics（分析）“调试”模式，请执行以下命令行：
```bash
adb shell setprop debug.firebase.analytics.app com.rolling.crossword.puzzle.game
```
“调试”模式将保持启用状态，直至您通过执行以下命令行明确停用“调试”模式：
```bash
adb shell setprop debug.firebase.analytics.app .none.
```
iOS
要在开发设备上启用 Analytics（分析）“调试”模式，请在 Xcode 中指定以下命令行参数：
-FIRDebugEnabled
“调试”模式将保持启用状态，直至您通过指定以下命令行参数明确停用“调试”模式：
-FIRDebugDisabled

## Android 安装bundle包导出的apks
```bash
java -jar bundletool.jar install-apks --apks=/MyApp/my_app.apks
```
[https://developer.android.com/studio/command-line/bundletool](https://developer.android.com/studio/command-line/bundletool)

## Unity 使用Script Define Symbols 实现条件编译
在Unity3D Player Settings  中可以定义 Script Define Symbols，其中定义的标签可以在代码中像Unity预定义标签（比如UNITY_EDITOR）一样访问，用作编译条件。可以用这种方式来更安全地控制是否启用调试模式：
比如，可以定义一个标签 DEV_DEBUG，标记是否开启调试模式，然后在代码中使用这个标签判断是否要开启日志输出
```C#
#if DEV_DEBUG
    public const bool logEnabled = true;
#else
    public const bool logEnabled = false;
#endif
```

这样，程序员可以在自己的Unity3D Player Settings中设置 Script Define Symbols 中，增加标签 DEV_DEBUG，那么在本地编译时就可以打开日志开关，而在编译服务器的编译脚本中不设置这个标签，则正式出包时就不会打开日志开关。

# Shell / Bash

## Shell 脚本获取当前日期时间
```bash
time=$(date "+%Y%m%d-%H%M%S")
time=$(date "+%Y-%m-%d %H:%M:%S")
echo "${time}"
```
上面两行简单的代码就是shell获取当前时间并按照自己想要的格式输出。
需要注意几点
date后面有一个空格，否则无法识别命令，shell对空格还是很严格的。
Y显示4位年份，如：2018；y显示2位年份，如：18。m表示月份；M表示分钟。d表示天，而D则表示当前日期，如：1/18/18(也就是2018.1.18)。H表示小时，而h显示月份(有点懵逼)。s显示当前秒钟，单位为毫秒；S显示当前秒钟，单位为秒。
```bash
sudo chmod+x post-commit
```
## 查看证书信息
```bash
keytool -printcert -file ./META-INF/CERT.RSA
```

