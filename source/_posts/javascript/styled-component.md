---
title: styled-component 工作原理
date: 2018-06-10 21:16:21
tags: [javascript, css-in-js]
categories: javascript
---

参考原文: [https://medium.com/styled...](https://medium.com/styled-components/how-styled-components-works-618a69970421)

在 React 的前端开发生态中，css-in-js 越来越常见了。[styled-component](https://github.com/styled-components/styled-components) 是其中使用最多的 css-in-js 库。这篇就介绍一下 styled-component 的工作原理。

## 特性

- 基于[标签模板(tagged_templates)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#tagged_templates)的语法
- 以编写 React 组件的形式来定义样式
- 解决了 CSS 模块化的问题，并提供了 CSS 嵌套
- 无需再为 css 类名而苦恼

## 标签模板( Tagged Templates)

首先需要了解下 标签模板(tagged_templates) 的语法。 这是 ES6 的一个新特性, 和 styled-components 没有直接关系，它只是使用了这种新语法而已。 直接上一个 🌰：

<!--more-->

```js
let person = "Mike";
let age = 28;

function myTag(strings, personExp, ageExp) {
  let str0 = strings[0]; // "That "
  let str1 = strings[1]; // " is a "
  let str2 = strings[2]; // "."

  let ageStr;
  if (ageExp > 99) {
    ageStr = "centenarian";
  } else {
    ageStr = "youngster";
  }

  // We can even return a string built using a template literal
  return `${str0}${personExp}${str1}${ageStr}${str2}`;
}

let output = myTag`That ${person} is a ${age}.`;

console.log(output);
// That Mike is a youngster.
```

可以用模板字符串(Template_literals) 来调用函数，其中 raw 字符串的部分作为函数的第一个 string 数组入参，插值部分按顺序依次作为后面的入参。

## styled-components 语法

先看下如何用 styled-components 定义一个 React 组件，也直接上 🌰 吧：

```js
const Button = styled.button`
  color: #333;
  border: solid 2px coral;
  border-radius: 3px;
  font-size: 14px;
`;
```

这里 styled.button 只是 styled('button') 的简写, styled 方法接收一个 html 标签名称(button)作为参数。其实 button 只是一个函数, 可以接收一个字符串数组作为参数. 类似下面的代码:

```js
// 定义
const styled = {
  button: function(strings, ...args){
    ....
  }
}
```

可以看到其实 styled 就是一个组件工厂, 接下来我们自己试着实现一下.

## 实现 styled-components

```js
const myStyled =
  TargetComponent =>
  ([style]) =>
    class extends React.Component {
      componentDidMount() {
        this.element.setAttribute("style", style);
      }

      render() {
        return (
          <TargetComponent
            {...this.props}
            ref={element => (this.element = element)}
          />
        );
      }
    };

const Button = myStyled.button`
  color: #333;
  border: solid 2px coral;
  border-radius: 3px;
  font-size: 14px;
`;
```

myStyled 工厂函数基于给定的标签名创建了一个新的组件, 在组件挂载之后设置行内样式。但这里还缺少一个用 props 为 style 字符串做插值的功能。

```js
const primaryColor = "coral";

const Button = styled("button")`
  color: ${({ primary }) => (primary ? primaryColor : "white")};
  border: solid 2px ${primaryColor};
  border-radius: 3px;
  font-size: 14px;
`;
```

如果要支持 props 做插值，myStyled 需要做如下修改:

```js
const myStyled =
  TargetComponent =>
  (strs, ...exprs) =>
    class extends React.Component {
      interpolateStyle() {
        const style = exprs.reduce((result, expr, index) => {
          const isFunc = typeof expr === "function";
          const value = isFunc ? expr(this.props) : expr;

          return result + value + strs[index + 1];
        }, strs[0]);

        this.element.setAttribute("style", style);
      }

      componentDidMount() {
        this.interpolateStyle();
      }

      componentDidUpdate() {
        this.interpolateStyle();
      }

      render() {
        return (
          <TargetComponent
            {...this.props}
            ref={element => (this.element = element)}
          />
        );
      }
    };
```

<code>interpolateStyle</code> 是插值的关键。我们把所有的字符串片段拼接得到 result; 如果某个插值是函数类型, 那么就会把组件的 props 传递给它, 同时调用函数。

但是实际上 styled-components 的底层实现更加有意思: 它不用内联样式. 让我们走近 styled-components 以了解创建组件的时候究竟发生了什么。

## styled-components 底层原理

**引入 styled-components**

当你首次引入 styled-components 库的时候, 它内部会创建一个 counter 变量, 用来记录每一个通过 styled 工厂函数创建的组件.

**调用 styled.tag-name 工厂函数**
styled-components 创建新组件的同时会给该组件创建一个 componentId 标识符. 代码如下:

```js
counter++;
const componentId = "sc-" + hash("sc" + counter);
```

第一个创建的 styled-components 组件的 componentId 为 <code>sc-bdVaJa</code>

一般情况下 styled-components 会使用 MurmurHash 算法创建唯一的标识符, 接着将 哈希值转化为乱序字母组成的字符串。

一旦创建好标识符, styled-components 会将 \<style\> 元素插入到 \<head\> 内部, 并且插入一条带有 componentId 的注释, 就像下面这样:

```js
<style data-styled-components>/* sc-component-id: sc-bdVaJa */</style>
```

创建好新组件之后, componentId 和 target 都会以静态属性的形式存储于 button 这个组件上:

```js
StyledComponent.componentId = componentId;
StyledComponent.target = TargetComponent;
```

可以看到, 仅仅创建一个 styled-components 组件, 并不会消耗太多性能. 甚至如果你定义了成百上千的组件而不去使用它们, 你最终得到的也只是一个或多个带有注释的 \<style\> 元素.

通过 styled 工厂函数创建的组件有个很重要的点: 它们都继承了一个隐藏的 <code>BaseStyledComponents</code> 类, 这个类实现了一些生命周期方法. 让我们看一下.

<code>componentWillMount()</code>

我们给 Button 组件创建一个实例并挂载到页面上:

```js
const Button = styled.button`
  font-size: ${({ sizeValue }) => sizeValue + "px"};
  color: coral;
  padding: 0.25rem 1rem;
  border: solid 2px coral;
  border-radius: 3px;
  margin: 0.5rem;
  &:hover {
    background-color: bisque;
  }
`;

ReactDOM.render(
  <Button sizeValue={24}>I'm a button</Button>,
  document.getElementById("root")
);
```

<code>BaseStyledComponents</code> 组件的 <code>componentWillMount()</code> 生命周期被调用了, 这释放了一些重要信号:

解析标记模板: 这个算法和我们实现过的 myStyled 工厂很相似. 对于 Button 组件的实例:
我们得到了如下所示的 CSS 样式字符串:

```css
font-size: 24px;
color: coral;
padding: 0.25rem 1rem;
border: solid 2px coral;
border-radius: 3px;
margin: 0.5rem;
&:hover {
  background-color: bisque;
}
```

**生成 CSS 类名**: 每个组件实例都会有一个唯一的 CSS 类名, 这个类名也是基于 MurmurHash 算法、componentId 以及 evaluatedStyles 字符串生成的:

```js
const className = hash(componentId + evaluatedStyles);
```

所以我们的 Button 实例生成的 className 是 jsZVzX.

之后这个类名会保存到组件的 state 上, 字段名为 <code>generatedClassName</code>.

**预处理 CSS**: 我们使用流行的 CSS 预处理器——stylis, 提取 CSS 字符串:

```js
const selector = "." + className;
const cssStr = stylis(selector, evaluatedStyles);
```

下面是 Button 实例最终的 CSS 样式:

```css
.jsZVzX {
  font-size: 24px;
  color: coral;
  padding: 0.25rem 1rem;
  border: solid 2px coral;
  border-radius: 3px;
  margin: 0.5rem;
}
.jsZVzX:hover {
  background-color: bisque;
}
```

**将 CSS 字符串注入到页面上**: 现在可以将 CSS 注入到 \<style\> 标签内部的带有组件标识注释的后面:

```css
<style data-styled-components>
  /* sc-component-id: sc-bdVaJa */
  .sc-bdVaJa {} .jsZVzX{font-size:24px;color:coral; ... }
  .jsZVzX:hover{background-color:bisque;}
</style>
```

正如你看到的, styled-components 也将 componentId(.sc-bdVaJa) 注入到页面上, 并且没有给 .sc-bdVaJa 定义样式.

当完成 CSS 的相关工作后, styled-components 只需要去创建组件的类名(className)即可:

```js
const TargetComponent = this.constructor.target; // In our case just 'button' string.
const componentId = this.constructor.componentId;
const generatedClassName = this.state.generatedClassName;

return (
  <TargetComponent
    {...this.props}
    className={
      this.props.className + " " + componentId + " " + generatedClassName
    }
  />
);
```

styled-components 给渲染的元素(TargetComponent)添加了 3 个类名:

1. this.props.className —— 从父组件传递过来的类名, 是可选的.
2. componentId —— 一个组件唯一的标识, 但是要注意不是组件实例. 这个类名没有 CSS 样式, 但是当需要引用其它组件的时候, 可以作为一个嵌套选择器来使用.
3. generatedClassName —— 具有 CSS 样式的组件的唯一前缀

最终渲染出来的 HTML 是这样的:

```jsx
<button class="sc-bdVaJa jsZVzX">I'm a button</button>
```

<code>componentWillReceiveProps()</code>

现在让我们尝试着在 Button 组件挂载完成之后更改它的 props. 需要做的是给 Button 组件添加一个交互式的事件:

```js
let sizeValue = 24;

const updateButton = () => {
  ReactDOM.render(
    <Button sizeValue={sizeValue} onClick={updateButton}>
      Font size is {sizeValue}px
    </Button>,
    document.getElementById("root")
  );
  sizeValue++;
};

updateButton();
```

你点击一次按钮, <code>componentWillReceiveProps()</code> 会被调用, 并且 sizeValue 会自增, 之后的流程和 componentWillMount() 一样:

- 解析标记模板
- 生成新的 CSS 类名
- stylis 预处理样式
- 将 CSS 注入到页面上

在多次点击按钮之后查看浏览器开发者工具, 可以看到:

```css
<style data-styled-components>
  /* sc-component-id: sc-bdVaJa */
  .sc-bdVaJa {}
  .jsZVzX{font-size:24px;color:coral; ... } .jsZVzX:hover{background-color:bisque;}
  .kkRXUB{font-size:25px;color:coral; ... } .kkRXUB:hover{background-color:bisque;}
  .jvOYbh{font-size:26px;color:coral; ... } .jvOYbh:hover{background-color:bisque;}
  .ljDvEV{font-size:27px;color:coral; ... } .ljDvEV:hover{background-color:bisque;}
</style>
```

是的, 所有类只有 font-size 属性不同, 并且无用的 CSS 类都没有被移除. 这是为什么? 因为移除无用的类会增加性能开销, 具体可以看 [这个解释](https://github.com/styled-components/styled-components/issues/1431#issuecomment-358097912).

这里有个小的优化点: 可以添加一个 isStatic 变量, 在 componentWillReceiveProps() 检查这个变量, 如果组件不需要插入样式的话, 直接跳过, 从而避免不必要的样式计算.

## 性能优化技巧

了解了 styled-components 底层是如何工作的, 之后才能更好的专注于性能优化.
如果要频繁的插不同的值，进而生成新的 css 类名的话，可以考虑使用 attrs 方法

```js
const Button = styled.button.attrs({
  style: ({ sizeValue }) => ({ fontSize: sizeValue + "px" }),
})`
  color: coral;
  padding: 0.25rem 1rem;
  border: solid 2px coral;
  border-radius: 3px;
  margin: 0.5rem;
  &:hover {
    background-color: bisque;
  }
`;
```

然而, 并不是所有的动态样式都应该采取这种方式. 我自己的规则是对于起伏比较大的数值, 使用 style 属性。但是, 如果你的按钮是多样化的, 比如 default、primary、warn 等, 还是使用样式字符串比较好.

在下面的例子里面, 我使用的是开发版本的 styled-components 包, 而你应该使用速度更快的生产版本. 在 React 项目里面, styled-components 的生产包禁用了很多开发环境下的警告, 这些警告是很重要的, 它使用 [CSSStyleSheet.insertRule()](https://developer.mozilla.org/en-US/docs/Web/API/CSSStyleSheet/insertRule) 将生成的样式注入到页面上, 但是开发环境下却用了 Node.appendChild()(Evan Scott [在这里](https://medium.com/styled-components/v3-1-0-such-perf-wow-many-streams-c45c434dbd03) 展示了 insertRule 到底有多快)

同时你也可以考虑使用 <code>babel-plugin-styled-components</code> 插件, 它可以压缩并预处理样式文件.

在这篇文章里面, 我使用的 styled-components 版本是 v3.3.3. 在后续的版本中它的源码可能会发生变化.
