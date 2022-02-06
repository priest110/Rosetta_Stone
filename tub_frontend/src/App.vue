<template>
  <v-app>
    <v-app-bar app color="#007DAB" dark>
      <div class="d-flex align-center">
        <!-- <v-img alt="Vuetify Logo" class="shrink mr-2" contain src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png" transition="scale-transition" width="40"/> -->

        <!-- <v-img alt="Vuetify Name" class="shrink mt-1 hidden-sm-and-down" contain min-width="100" src="https://cdn.vuetifyjs.com/images/logos/vuetify-name-dark.png" width="100"/> -->
      </div>

      <v-spacer></v-spacer>

      <v-btn href="https://tub.pt/" target="_blank" text>
        <span class="mr-2">{{ agency.agency_name }}</span>
      </v-btn> 
    </v-app-bar>
  
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script> 

export default {
  name: 'App',

  data: () => ({
      agency: [],
  }),

  created() {
      this.fetch_agency()
  },

  methods: {
      async fetch_agency(){
        var aux
        await fetch("http://localhost:1337/api/agencies")
          .then(response => response.json())
          .then(data => aux = data.data.map(obj => obj['attributes']))
        this.agency = aux.find(obj => {
          return obj['agency_id'] === "TUB"
        })
        //console.log(this.agencies[0])
      },
  }
};
</script>
