---
title: redux 源码分析【4.0.0-beta.2】
date: 2018-03-16 21:58:38
tags: 源码解析
categories: javascript
---

[redux](http://redux.js.org/) 一个可预测的 js 状态容器（Predictable state container for JavaScript apps）, 在很多 React 项目中都会默认使用 react-redux 作为全局状态管理工具。

让我们先来看下源码仓库暴露出来的方法。redux 库一共导出如下几个方法 createStore, combineReducers, bindActionCreators, applyMiddleware, compose, DO_NOT_USE\_\_ActionTypes。

## createStore

先看下 createStore。 createStore 接受三个参数：reducer, preloadedState, enhancer

<!--more-->

```js
/**
 * Creates a Redux store that holds the state tree.
 * The only way to change the data in the store is to call `dispatch()` on it.
 *
 * There should only be a single store in your app. To specify how different
 * parts of the state tree respond to actions, you may combine several reducers
 * into a single reducer function by using `combineReducers`.
 *
 * @param {Function} reducer A function that returns the next state tree, given
 * the current state tree and the action to handle.
 *
 * @param {any} [preloadedState] The initial state. You may optionally specify it
 * to hydrate the state from the server in universal apps, or to restore a
 * previously serialized user session.
 * If you use `combineReducers` to produce the root reducer function, this must be
 * an object with the same shape as `combineReducers` keys.
 *
 * @param {Function} [enhancer] The store enhancer. You may optionally specify it
 * to enhance the store with third-party capabilities such as middleware,
 * time travel, persistence, etc. The only store enhancer that ships with Redux
 * is `applyMiddleware()`.
 *
 * @returns {Store} A Redux store that lets you read the state, dispatch actions
 * and subscribe to changes.
 */

 export default function createStore(reducer, preloadedState, enhancer) {
   ...
 }
```

并最终返回一个 state 对象：

```js
...

// When a store is created, an "INIT" action is dispatched so that every
// reducer returns their initial state. This effectively populates
// the initial state tree.
dispatch({ type: ActionTypes.INIT })

return {
  dispatch,
  subscribe,
  getState,
  replaceReducer,
  [$$observable]: observable
}

```

**subscribe** 函数：接受一个 listener 参数，然后将其推入 listener 数组 **nextListeners.push(listener)**，
最终返回一个 **unsubscribe** 函数来解除订阅。

**dispatch** 函数：接受一个 action 参数，action 最好是可序列化的对象，并且必须有一个非 undefined 的 type 属性 。

**dispatch** 函数主要做两件事情：

1. 执行 reducer，返回新的 state tree。
2. 通知(执行)订阅的 listeners。

```js
try {
  isDispatching = true;
  currentState = currentReducer(currentState, action);
} finally {
  isDispatching = false;
}

const listeners = (currentListeners = nextListeners);
for (let i = 0; i < listeners.length; i++) {
  const listener = listeners[i];
  listener();
}
```

**replaceReducer** 函数：接受一个新的 reducer 来替换老的 reducer, 主要用在 code splitting 和 hot reloading 的情况下

**observable** 函数: 这个函数可以认为是对接 observable/reactive 类库的接口，比如 RxJS。
关于 observable 可以看下这篇文章:[RxJS: 如何从头开始创建 Observable](https://zhuanlan.zhihu.com/p/27776484)

## combineReducers

```js
/**
 * Turns an object whose values are different reducer functions, into a single
 * reducer function. It will call every child reducer, and gather their results
 * into a single state object, whose keys correspond to the keys of the passed
 * reducer functions.
 *
 * @param {Object} reducers An object whose values correspond to different
 * reducer functions that need to be combined into one. One handy way to obtain
 * it is to use ES6 `import * as reducers` syntax. The reducers may never return
 * undefined for any action. Instead, they should return their initial state
 * if the state passed to them was undefined, and the current state for any
 * unrecognized action.
 *
 * @returns {Function} A reducer function that invokes every reducer inside the
 * passed object, and builds a state object with the same shape.
 */
export default function combineReducers(reducers) {}
```

最终返回的是结合后的 reducer ：

```js
return function combination(state = {}, action) {
  ...

  let hasChanged = false
  const nextState = {}
  for (let i = 0; i < finalReducerKeys.length; i++) {
    const key = finalReducerKeys[i]
    const reducer = finalReducers[key]
    const previousStateForKey = state[key]
    const nextStateForKey = reducer(previousStateForKey, action)
    if (typeof nextStateForKey === 'undefined') {
      const errorMessage = getUndefinedStateErrorMessage(key, action)
      throw new Error(errorMessage)
    }
    nextState[key] = nextStateForKey
    hasChanged = hasChanged || nextStateForKey !== previousStateForKey
  }
  return hasChanged ? nextState : state
}
```

从上面的代码可以看出每个 reducer 会接受对应 key 的 state subtree(并不是整个 state object)以及 action 对象作为入参，返回的结果最终组合成一个新的 state。

另外, 返回的 combination 函数的签名和单个 reducer 是一样的，这样就可以嵌套的使用 combineReducers， 比如:

```js
const combinedReducer = combineReducers({
  reducer1,
  reducer2,
  combineReducers({
    reducer3,
    reducer4
  })
})
```

## bindActionCreators

```js
/**
 * Turns an object whose values are action creators, into an object with the
 * same keys, but with every function wrapped into a `dispatch` call so they
 * may be invoked directly. This is just a convenience method, as you can call
 * `store.dispatch(MyActionCreators.doSomething())` yourself just fine.
 *
 * For convenience, you can also pass a single function as the first argument,
 * and get a function in return.
 *
 * @param {Function|Object} actionCreators An object whose values are action
 * creator functions. One handy way to obtain it is to use ES6 `import * as`
 * syntax. You may also pass a single function.
 *
 * @param {Function} dispatch The `dispatch` function available on your Redux
 * store.
 *
 * @returns {Function|Object} The object mimicking the original object, but with
 * every action creator wrapped into the `dispatch` call. If you passed a
 * function as `actionCreators`, the return value will also be a single
 * function.
 */
export default function bindActionCreators(actionCreators, dispatch) {}
```

需要注意的几点:

<code>For any unknown actions, you must return the current state. If the current state is undefined, you must return the initial state. The initial state may not be undefined. If you don't want to set a value for the reducer, you can use null instead of undefined</code>

## compose

**compose** 是一个工具函数，接受多个函数作为参数，返回一个组合后的函数。 compose(f, g, h) 会返回 (…args) => f(g(h(…args))).

## applyMiddleware

<code>applyMiddleware(...middlewares)</code> 函数返回一个 store enhancer，可以作为 createStore 的第三个参数

```js
export default function applyMiddleware(...middlewares) {
  return createStore =>
    (...args) => {
      const store = createStore(...args);
      let dispatch = () => {
        throw new Error(
          `Dispatching while constructing your middleware is not allowed. ` +
            `Other middleware would not be applied to this dispatch.`
        );
      };
      let chain = [];

      const middlewareAPI = {
        getState: store.getState,
        dispatch: (...args) => dispatch(...args),
      };
      chain = middlewares.map(middleware => middleware(middlewareAPI));
      dispatch = compose(...chain)(store.dispatch);

      return {
        ...store,
        dispatch,
      };
    };
}
```

middleware 的函数签名为: <code>({ dispatch, getState }) => next => action => { return next(...) }</code>:

middleware 先接受 { dispatch, getState } 对象做为入参，然后再通过 compose 函数接受 dispatch 作为入参，将之前 compose 的执行顺序又反了过来，middleware 的执行顺序为从左往右，执行 next 函数其实是下一个 middleware。但最后一个 middleware 的 next 实际上是原始的 store.dispatch 函数。最终用 compose 的 dispatch 函数替换原先 createStore 返回的 dispatch。于是，新的 dispatch 就可以根据参数的类型来做处理，如果参数符合则进行逻辑处理，如果不符合则 <code>return next(arguments)</code> 来执行下一个 middleware 。

比如 redux-thunk 这个 middleware，源码如下:

```js
function createThunkMiddleware(extraArgument) {
  return ({ dispatch, getState }) =>
    next =>
    action => {
      if (typeof action === "function") {
        return action(dispatch, getState, extraArgument);
      }

      return next(action);
    };
}

const thunk = createThunkMiddleware();
thunk.withExtraArgument = createThunkMiddleware;

export default thunk;
```

可以看到 middleware 的签名确实是这样的。
另外需要注意，middleware 内部的 dispatch 函数其实也是 compose 后的 dispatch，并不是原始的 store.dispatch, 所以执行 dispatch 时会再次进入每个 middleware。比如 thunk，dispatch 一个 fetch 函数，在 fetch 执行获得 response 后，可以再次 dispatch 另一个 fetch：

```js
const fetch1 = dispatch =>
  fetch({ url: url1 }).then(res => {
    dispatch({
      type: "FETCH1",
      payload: res,
    });
  });

const fetch2 = dispatch =>
  fetch({ url: url2 }).then(res => {
    dispatch(fetch1); // 再次进入 middleware
  });

const getFetchResp = dispatch => {
  dispatch(fetch2);
};
```

至此，redux 4.0.0-beta2 版本的源码就解析完了，其中概念的东西占的较多，所以上还是需要理解作者的设计思路，这样也有利于理解源码的逻辑
