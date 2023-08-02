// 获取CSRF令牌的函数
function getCSRFToken() {
  const cookieValue = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
  return cookieValue ? cookieValue.pop() : '';
}

// 创建axios实例
const instance = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 设置API的基础URL
  timeout: 10000, // 请求超时时间
});

// 请求拦截器，添加CSRF令牌到请求头
instance.interceptors.request.use(function (config) {
  config.headers['X-CSRFToken'] = getCSRFToken();
  return config;
}, function (error) {
  return Promise.reject(error);
});

// 封装GET请求
function axiosGet(url, params) {
  return instance.get(url, { params })
    .then(response => response.data)
    .catch(error => {
      console.error(error);
      throw error;
    });
}


// 封装POST请求
function axiosPost(url, data) {
  return instance.post(url, data)
    .then(response => response.data)
    .catch(error => {
      console.error(error);
      throw error;
    });
}

// 封装DELETE请求
function axiosDel(url, params) {
  return instance.delete(url, { params })
    .then(response => response.data)
    .catch(error => {
      console.error(error);
      throw error;
    });
}

// 封装PUT请求
function axiosPut(url, data) {
  return instance.put(url, data)
    .then(response => response.data)
    .catch(error => {
      console.error(error);
      throw error;
    });
}
