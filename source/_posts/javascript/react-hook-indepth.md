---
title: React Hook 工作原理
date: 2019-11-05 20:12:20
tags: React
categories: javascript
---

## 前言

自从 react 推出 hook 后就一直觉得 hook 的实现挺神秘的，这篇文章主要记录下自己对 react hook 底层实现的理解，并用代码模拟下 react hook 的实现原理。

## useState

useState 可以说是整个 hook 的基础，它使得函数组件也拥有自己的状态。使用起来很简单:

```js
const [count, setCount] = useState(0);
```

那么我们可以先简单的按自己的理解实现一下 useState 的逻辑：

<!--more-->

```js
function useState(initialState) {
  const state = initialState;
  const setState = newState => (state = newState);
  return [state, setState];
}
```

当然上面的实现是有明显问题的。因为他无法记住数据，每次调用 setState，都会返回传入的初始化值，而无法拿到上一次执行的结果。所以需要有一个机制把 state 保存起来。

当然可以用全局变量来保存，但 react 并不是这样做的。react 用的是数组:

```js
const HOOKS = []; // 全局存储 hook 的数组
let currentIndex = 0; // 全局 hook 执行顺序的下标

function useState(initialState) {
  HOOKS[currentIndex] = HOOKS[currentIndex] || initialState; // 判断是否需要初始化
  const memoryCurrentIndex = currentIndex; // 这里先存一个局部变量
  const setState = newState => (HOOKS[memoryCurrentIndex] = newState); // 局部函数使用了闭包
  return [HOOKS[currentIndex++], setState];
}
```

修改后的版本，首先从全局 HOOKS 数组里读取 state 存下来的值，然后使用了**内部函数的闭包**，是的 setState 函数内指向的 memoryCurrentIndex 顺序不会变。

另外，可以看到每次调用 useState 都是去找对应的下标，**这也是为什么要保证 hooks 的执行顺序在更新前后一致的原因**。

useState 还可以传函数，那么我们也扩展下实现来支持传入函数:

```js
function useState(initialState) {
  HOOKS[currentIndex] =
    HOOKS[currentIndex] ||
    (typeof initialState === "function" ? initialState() : initialState);
  const memoryCurrentIndex = currentIndex;
  const setState = p => {
    let newState = p;
    if (typeof p === "function") {
      newState = p(HOOKS[memoryCurrentIndex]);
    }
    if (newState === HOOKS[memoryCurrentIndex]) return;
    HOOKS[memoryCurrentIndex] = newState;
  };
  return [HOOKS[currentIndex++], setState];
}
```

## useEffect

useEffect 等价于 class 组件中 <code>componentDidMount</code> 和 <code>componentDidUpdate</code> 两个生命周期函数。更多地用来通知更新，执行副作用函数等。useEffect 的原理和 useState 很相似，只是多了一个依赖数组：

```js
function useEffect(fn, deps) {
  const hook = HOOK[currentIndex];
  const _deps = hook && hook._deps;
  const memoryCurrentIndex = currentIndex;
  const hasChanged = _deps ? !deps.every((v, i) => _deps[i] === v) : true;
  if (hasChanged) {
    // 执行上次的 effect 返回的清理函数
    const _effect = hook && hook._effect;
    setTimeout(() => {
      typeof _effect === "function" && _effect();
      // 执行本次的
      const ef = fn();
      HOOKS[memoryCurrentIndex] = { ...HOOKS[memoryCurrentIndex], _effect: ef };
    });
  }
  HOOKS[currentIndex++] = { _deps: deps, _effect: null };
}
```

这里的 hook 是一个对象，保存了两个属性，分别是依赖 deps 和 sideEffect 的清理函数。因为 useEffect 需要在 dom 挂载后再执行，因为这里只是演示，所以用了 setTimeout 简单模拟，React 中不是这样。

## useReducer

useReducer 比较简单，只是对 useState 做了简单的包装， 先看下如何使用：

```js
const reducer = (state, action) => {
  switch (action.type) {
    case "increment":
      return { ...state, total: state.total + 1 };
    case "decrement":
      return { ...state, total: state.total - 1 };
    default:
      throw Error();
  }
};

const [state, dispatch] = useReducer(reducer, { total: 0, date: Date.now() });
```

具体实现的话结合 useState 和 reducer 就可以：

```js
function useReducer(reducer, initialState) {
  const [state, setState] = useState(initialState);
  const dispatch = action => {
    const newState = reducer(state, action);
    setState(newState);
  };
  return [state, disptach];
}
```

## useMemo

useMemo 是用来提高函数组件性能的 hook， 主要针对处理一些消耗大的计算。

```js
function useMemo(fn, deps) {
  const hook = HOOKS[curretIndex];
  const _deps = hooks && hooks._deps;
  const hasChanged = _deps ? _deps.every((v, i) => v === deps[i]) : true;
  const memo = hasChanged ? fn() : hooks.memo;
  HOOKS[curretIndex++] = { _deps: deps, memo };
  return memo;
}
```

## useCallback

和 useMemo 类似，useMemo 会返回一个值，而 useCallback 会返回一个函数。

```js
function useCallback(fn, deps) {
  return useMemo(() => fn, deps);
}
```

## 参考文章

[Deep dive: How do React hooks really work?](https://www.netlify.com/blog/2019/03/11/deep-dive-how-do-react-hooks-really-work/)
[深入 React hooks — 原理 & 实现](https://zhuanlan.zhihu.com/p/88734130)
[React Hooks Not Magic, Just Arrays](https://medium.com/@ryardley/react-hooks-not-magic-just-arrays-cd4f1857236e)
