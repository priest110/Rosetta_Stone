<template>
  <div id='google-map'>
    <v-row class="mt-5">
      <v-col cols="10">
        <h3>Pretendes visualizar o mapa de determinado itinerário? Escolhe qual através do código do percurso respetivo <v-icon>mdi-arrow-right-thin</v-icon></h3>
      </v-col>
      <v-col>
        <v-select v-model="first_code" class="mt-n4 ml-n7" :items="code" :menu-props="{ top: true, offsetY: true }" label="Código do percurso" @change="render_shape()"></v-select>
      </v-col>
    </v-row>
    <br>
    <GmapMap
      :center='center'
      :zoom='12'
      style='width:100%;  height: 400px;'
    >
      <GmapPolyline 
        v-bind:path.sync="path" v-bind:options="{ strokeColor:'#0000FF'}"
      />

      <div v-for="(m, index) in markers" :key="index">
        <div v-if="m.type == 0">
          <GmapMarker
            :position="m.position"
            :clickable="true"
            :draggable="false"
            @click="center=m.position"
            :icon="markerOptions"
          />
        </div>
        <div v-if="m.type == 1">
          <GmapMarker
            :position="m.position"
            :clickable="true"
            :draggable="false"
            @click="center=m.position"
            :icon="markerOptions_selected"
          />
        </div>
      </div>
    </GmapMap>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'GoogleMap',
  props: ['code', 'trips', 'direction', 'principal_spots', 'stop_click', 'shapes', 'stops_by_trip'],
  watch: {
        stop_click: function(newVal, oldVal) {
          this.markers = [...this.markers_default]

          console.log("Prop changed: " + JSON.stringify(newVal) + "| was " + oldVal)

          var code_aux = this.first_code.substring(1)
          var trip_id = this.trips[code_aux - 1].trip_id

          var stop_aux = this.stops_by_trip.filter(obj => {
          return obj['trip_id'] === trip_id && obj['stop_id'] === newVal.stop_id
          })
          if(stop_aux.length > 0) {
            const pos = { lat: newVal.lat, lng: newVal.lng }
            var aux = this.markers.findIndex(obj => {
              return obj['position']['lat'] === pos.lat && obj['position']['lng'] === pos.lng
            })
            console.log("entrou")
            Vue.set(this.markers, aux, {position: pos, type:1})
          }
          console.log(this.markers_default)
          console.log(this.markers)
        }
  },
  
  data() {
    return {
      first_code: 'M1',
      center: { lat: 41.5454, lng: -8.4265 },
      path: [],
      markers: [],
      markers_default: [],
      markerOptions: {
        url: require('../assets/bus_stop.png'),
        size: {width: 35, height:45, f: 'px', b: 'px',},
        scaledSize: {width:40, height: 45, f: 'px', b: 'px',},
      },
      markerOptions_selected: {
        url: require('../assets/bus_stop_green.png'),
        size: {width: 35, height:45, f: 'px', b: 'px',},
        scaledSize: {width:35, height: 50, f: 'px', b: 'px',},
      },
    }
  },

  mounted() {
    this.geolocate();
  },
  
  created(){
    this.render_shape();
  },

  methods: {

    geolocate: function() {
      navigator.geolocation.getCurrentPosition(position => {
        this.center = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
      });
    },

    render_shape(){

      this.markers_default = []
      //reset array
      this.path = []

      var code_aux = this.first_code.substring(1)
      var shape = this.trips[code_aux-1].shape_id
      console.log("SHAPE:" + shape)
      console.log(code_aux)
      console.log(this.trips[code_aux-1])
      for (let i = 0; i < this.shapes.length; i++){
        if (this.shapes[i].shape_id == shape){

          this.path.push( { lat:  parseFloat(this.shapes[i].shape_pt_lat), 
                            lng:  parseFloat(this.shapes[i].shape_pt_lon),
                            "sequence" : parseInt(this.shapes[i].shape_pt_sequence) } )
        }
      }

      this.path.sort((a, b) => a.sequence - b.sequence)
      
      var trip_id = this.trips[code_aux - 1].trip_id
      console.log(this.principal_spots)

      for (let i = 0; i < this.principal_spots.length; i++){
        var stop_aux = this.stops_by_trip.find(obj => {
          return obj['trip_id'] === trip_id && obj['stop_id'] === this.principal_spots[i].stop_id
        })

        console.log(stop_aux)

        if(typeof stop_aux !== 'undefined') {
          const pos = { lat: this.principal_spots[i].stop_lat, lng: this.principal_spots[i].stop_lon }
          this.markers_default.push( { position: pos, type: 0 } )
        }
      }
      console.log(this.markers_default)
      this.markers = this.markers_default

    }
  },
}

</script>