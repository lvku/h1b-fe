import Vue from 'vue'
import App from './App.vue'

import VueChartkick from 'vue-chartkick'
import VueMaterial from 'vue-material'
import Chart from 'chart.js'
import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default.css' 

Vue.use(VueMaterial)
Vue.use(VueChartkick, {adapter: Chart})

Vue.config.productionTip = false

new Vue({
  render: h => h(App)
}).$mount('#app')
