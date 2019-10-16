---
layout:     post
title:      常用书签
subtitle:   开发
date:       2019-10-16
author:     Ping
header-img: img/post-bg-cook.jpg
catalog: true
tags:
    - Coding
    - Development
---

目录
[TOC]

* * *

# Unity3D 官方教程
[https://unity3d.com/cn/learn/tutorials](https://unity3d.com/cn/learn/tutorials)

[https://unity3d.com/cn/learn/tutorials/s/2d-roguelike-tutorial](https://unity3d.com/cn/learn/tutorials/s/2d-roguelike-tutorial)


## 脚本生命周期

[一张图说明Unity3d各种update的区别_包括Awake() Start() - 大话程序员 - CSDN博客](https://blog.csdn.net/avi9111/article/details/70429578)

## TextMeshPro  
* [组件介绍](http://digitalnativestudios.com/textmeshpro/docs/textmeshpro-component/)
* [RichText](http://digitalnativestudios.com/textmeshpro/docs/rich-text/#color)
* [中文组件介绍](https://blog.csdn.net/qq_33337811/article/details/79029733)


# Unity3D 动画和特效

## 缓动函数Easing Function 

[缓动函数速查表](http://www.xuanfengge.com/easeing/easeing/)

[本地笔记：缓动函数 Easing Function](https://app.yinxiang.com/shard/s27/nl/6947617/138651a7-a0a8-47ae-9e6f-8c66de08afaa/)

## 使用DOTween实现按钮缩放


```C#

using DG.Tweening

m_Button.transform.localScale = new Vector3(0, 0, 0);  //首先将按钮的尺寸设定为最小
m_Button.gameObject.SetActive(true);  // 一定要在设定最小尺寸之后再将Active的状态设置为True，否则可能看不到缩放的效果
m_Button.transform.DOScale( new Vector3(1, 1, 1), 0.8f ).SetEase(Ease.OutBounce).OnComplete(
        delegate ()
        {
            //注意：如果控件上Attach有其他预定的AnimationController，那么DOTween动画不会播放，需要在Editor里先禁用Animator，然后在DOTween动画播放完成后OnComplete()里启用
            m_Button.GetComponent<Animator>().enabled = true
            //Do somgthing after DOScale animation completed;
        });
````

# 性能优化

## 协程Yield return new WaitForXXX 带来的额外GC开销

```C#
void Start()
{
    StartCoroutine(OnEndOfFrame());
}

IEnumerator OnEndOfFrame()
{
    yield return null;

    while (true)
    {
        //Debug.LogFormat("Called on EndOfFrame.");
        yield return new WaitForEndOfFrame();
    }
}
```

上面的代码会导致 WaitForEndOfFrame 对象的每帧分配，给 GC 增加负担。假设游戏内有 10 个活跃协程，运行在 60 fps，那么每秒钟的 GC 增量负担是 10 * 60 * 16 = 9.6 KB/s。

我们可以简单地通过复用一个全局的 WaitForEndOfFrame 对象来优化掉这个开销：
```C#
static WaitForEndOfFrame _endOfFrame = new WaitForEndOfFrame();
```
然后调用yield return 时不创建新对象，而是复用该全局变量
```C#
yield return _endOfFrame;
```
这样就可以避免额外的GC开销，该方法适用于所有继承自 YieldInstruction 的用于挂起协程的指令类型，包括
* WaitForSeconds
* WaitForFixedUpdate
* WaitForEndOfFrame


[Android UI 切图命名规范、标注规范及单位描述](https://blog.csdn.net/klxh2009/article/details/74938009)
