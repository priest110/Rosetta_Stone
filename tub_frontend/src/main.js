import Vue from 'vue'
import App from './App.vue'
import * as VueGoogleMaps from 'vue2-google-maps'
import vuetify from './plugins/vuetify'
import { router } from './_helpers/router'

Vue.config.productionTip = false

Vue.use(VueGoogleMaps, {
  load: {
    key: 'AIzaSyAmrquHj5Yri21D9lDvb_vp2BJbgT6lPbU',
    libraries: 'places',
  }
});


new Vue({
  vuetify,
  router,
  render: h => h(App)
}).$mount('#app')
