const jsdom = require("jsdom");
const {JSDOM} = jsdom;
const dom = new JSDOM();
window = dom.window;
document = dom.document;
XMLHttpRequest = dom.XMLHttpRequest;

// 上面不变,在下面直接粘贴复制过来的代码
// atob 是浏览器反编译的函数，改成 window.atob 就可以

function myprint(...args) {
    let result = "";
    args.forEach(arg => {
        console.log(arg);  // 保持打印
        result += arg + "\n";  // 拼接字符串作为返回值
    });
    return result;  // 返回拼接后的字符串
}


