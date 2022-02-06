<template>
  <v-container v-if="loading">
    <v-row class="text-center">
      <v-col cols="2"/>

      <v-col cols="8">
        <v-card flat class="mt-5" fluid style="width:100%;">
          <v-row class="text-center header">
            <v-col cols="1">
              <v-btn icon color="white">
                <v-icon>
                  mdi-chevron-left
                </v-icon>
              </v-btn>
            </v-col>

            <v-col cols="10" class="mb-4">
              <v-row no-gutters>
                <v-col cols="4"/>
                <v-col cols="1">
                  <div class="display-1 font-weight-bold text-h2">
                    {{ parseInt(this.route['route_short_name'], 10) }}
                  </div>
                </v-col>
                <v-col>
                  <template v-if="this.route['route_long_name'] == this.route['route_long_name'].split(/\s*-\s*/)">
                    <div class="display-1 text-h6">
                      {{ this.route['route_long_name']}}
                    </div>
                  </template>
                  <template v-else>
                    <template v-if="this.direction == 0">
                      <div class="display-1 text-left text-h6">
                        {{ this.route['route_long_name'].split(/\s*-\s*/)[0]}}
                      </div>
                      <div class="display-1 text-left text-h6">
                        {{ this.route['route_long_name'].split(/\s*-\s*/)[1] }}
                      </div>
                    </template>
                    <template v-else>
                      <div class="display-1 text-left text-h6">
                        {{ this.route['route_long_name'].split(/\s*-\s*/)[1] }}
                      </div>
                      <div class="display-1 text-left text-h6">
                        {{ this.route['route_long_name'].split(/\s*-\s*/)[0]}}
                      </div>
                    </template>
                  </template>
                </v-col>
              </v-row>
            </v-col>      

            <v-col cols="1">
            </v-col>
          </v-row>
        </v-card>
      </v-col>

      <v-col cols="2">
        <v-btn @click="change_direction" class="text_color  d-flex justify-start mt-2" height="120"  >
          <v-flex class="vertical_button">
            <span class="white--text">
            IDA
            </span>
            <v-icon class="white--text">
            mdi-arrow-right-thin
            </v-icon>
            <v-icon class="white--text">
              mdi-bus-side
            </v-icon>
            <v-icon class="white--text">
              mdi-arrow-left-thin
            </v-icon>
            <span class="white--text">
              VOLTA
            </span>
          </v-flex>
        </v-btn>
      </v-col>
    </v-row>
    
    <v-row class="text-center">
      <v-col cols="2"/>
      
      <v-col cols="8">
          <v-tabs v-model="tab_first[direction]" class="rounded-lg" background-color="#d9ecf2" centered  fixed-tabs>
            <v-tabs-slider></v-tabs-slider>
            
            <v-tab v-for="(option, index) in calendar_options[direction]" :key="index" :href="'#tab-' + (index+1)">
                {{ option['type'] }}
            </v-tab> 
          </v-tabs>

          <v-tabs-items v-model="tab_first[direction]">
            <v-tab-item v-for="i in 3" :key="i" :value="'tab-' + i">
              <div class="table_specs mt-5">
                <table>           
                  <thead>
                    <tr>
                      <th style="width: 300px;min-width:300px; background: white;"/>
                    </tr>
                  </thead>
                  <tbody v-for="(stop,stop_index) in principal_spots_by_trip[direction][i-1]" :key="stop_index">
                    <tr class="principal_row">
                      <button text class="header_column" @click="handle(principal_spots_by_trip[direction][i-1],stop['stop_id'])">
                        {{ stop['stop_name'] }}
                      </button>
                      <td v-for="(st, st_index) in get_stop_times(trips_by_direction_schedule[direction][i-1], stops_by_trip[direction][i-1], stop)" :key="st_index">
                        <template v-if="st['timepoint'] == 0">
                            <v-icon v-if="(typeof st['icon_1'] !== 'undefined')" class="hidden_icon"  color="#007DAB">  
                              {{st['icon_1']}}
                            </v-icon>
                            <v-icon v-else-if="(typeof st['icon_2'] !== 'undefined')" class="hidden_icon"  color="#007DAB">  
                              {{st['icon_2']}}
                            </v-icon>
                            <span v-bind:class="st['color']" class="font-italic">
                              {{ st['departure_time'].substring(0,5) }}
                            </span>
                        </template>
                        <template v-else >
                          <v-icon v-if="(typeof st['icon_1'] !== 'undefined')" class="hidden_icon" color="#007DAB">  
                            {{st['icon_1']}}
                          </v-icon>
                          <v-icon v-else-if="(typeof st['icon_2'] !== 'undefined')" class="hidden_icon" color="#007DAB">  
                            {{st['icon_2']}}
                          </v-icon>
                          <span v-bind:class="st['color']">
                            {{ st['departure_time'].substring(0,5) }}
                          </span>
                        </template>
                      </td>
                    </tr>

                    <tr v-if="stop_index < principal_spots_by_trip[direction][i-1].length-1" class="button_row">
                      <th class="button_column">
                        <v-btn v-if="!show_options[direction][i-1][stop_index]" text small @click="show_intermediates(i-1, direction, stop_index)">[Mostrar paragens intermédias]</v-btn>
                        <v-btn v-else text small @click="show_intermediates(i-1, direction, stop_index)">[Fechar paragens intermédias]</v-btn>
                      </th>
                    </tr>
                    
                    <template v-if="show_options[direction][i-1][stop_index]">
                      <tr class="color_row" v-for="(intermediate_stop, intermediate_index) in intermediate_spots_by_trip[direction][i-1][stop_index]" :key="intermediate_index">
                        <th class="intermediate_column">{{ intermediate_stop['stop_name'] }}</th>
                        <td v-for="(st, st_index) in get_stop_times(trips_by_direction_schedule[direction][i-1], intermediate_spots_by_trip[direction][i-1][stop_index], intermediate_stop)" :key="st_index">
                          <template v-if="st['timepoint'] == 0">
                            <span  v-bind:class="st['color']" class="font-italic">
                              {{ st['departure_time'].substring(0,5) }}
                            </span>
                          </template>
                          <template v-else>
                            <span v-bind:class="st['color']">
                              {{ st['departure_time'].substring(0,5) }}
                            </span>
                          </template>
                        </td>
                      </tr>
                    </template> 

                    <template v-if="stop_index == principal_spots_by_trip[direction][i-1].length-1">
                        <tr class="code_row">
                          <th class="code_column">Código Percurso </th>
                          <td v-for="n in trips_by_direction_schedule[direction][i-1].length" :key="n"  class="white--text">
                            M{{n}}
                          </td>
                        </tr>
                    </template>  
                  </tbody>
                </table>
              </div>
              <v-card flat class="mt-3">
                <v-row>
                  <v-col cols="6">
                    <v-card-title>
                      <v-row>
                        <span class="reference_color">
                          Legenda
                        </span>
                      </v-row>
                    </v-card-title>
                    <v-card-text>
                      <v-row align="start" class="mt-0">
                        <v-icon>
                          mdi-alpha-p-circle
                        </v-icon>
                        <span class="ml-1 black--text">Partida</span>
                      </v-row>
                      <v-row align="start" >
                        <v-icon>
                          mdi-alpha-c-circle
                        </v-icon>
                        <span class="ml-1 black--text">Chegada</span>
                      </v-row>
                      <v-row align="start">
                        <span>"</span>
                        <span class="font-italic grey--text">
                          Horário em itálico
                        </span>
                        <span>"</span>
                        <span class="ml-1 black--text">com passagem nesta paragem, mas com horário incerto</span>
                      </v-row>
                      <v-row align="start">
                        <span>"</span>
                        <span class="font-weight-black"> -</span>
                        <span>"</span>
                        <span class="ml-1 black--text">sem passagem nesta paragem</span>
                      </v-row>
                    </v-card-text>
                  </v-col>
                  <v-col cols="6">
                    <v-card-title v-if="trip_notes_by_trip != null && trip_notes_by_trip[direction][i-1].length > 0">
                      <v-row>
                        <span class="reference_color">
                          Notas
                        </span>
                      </v-row>
                    </v-card-title>
                    <v-card-text v-if="trip_notes_by_trip != null && trip_notes_by_trip[direction][i-1].length > 0">
                      <v-row v-for="(note, indx) in trip_notes_by_trip[direction][i-1]" :key="indx" align="start" class="mt-0">
                        <span class="font-weight-black">
                          Percurso M{{note['M_index']}}:
                        </span>
                        <span class="ml-1 black--text">{{note['description']}}</span>
                      </v-row>
                    </v-card-text>
                  </v-col>
                </v-row>
              </v-card>
              
              <google-map :code="codes[direction][i-1]" :trips="trips_by_direction_schedule[direction][i-1]"  :principal_spots="principal_spots_by_trip[direction][i-1]" :stop_click="stop_click" :shapes="shapes_by_trip[direction][i-1]" :stops_by_trip="stops_by_trip[direction][i-1]"/>                           
            </v-tab-item>
          </v-tabs-items>
      </v-col>

      <v-col cols="2"/>
    </v-row> 
  </v-container>
  
</template>

<script>
  import Vue from 'vue'
  import GoogleMap from './GoogleMap.vue'

  export default {
    name: 'RoutePage',

    components:{
      GoogleMap
    }, 

    data: () => ({
      route: {},
      direction: 0,
      trips: [],
      lines: [],
      shapes: [],
      trips_by_direction_schedule : [[], []],
      trip_notes_by_trip: [[], []],
      stops_by_trip: [[], []],
      principal_spots_by_trip: [[], []],
      intermediate_spots_by_trip: [[], []],
      shapes_by_trip: [[], []],
      trip_notes: [],
      stop_times: [],
      stops: [],
      calendar: [],
      calendar_dates: [],
      tab_first: [],
      calendar_options: [[], []],
      show_options: [[], []],
      loading: false,
      codes: [[], []],
      stop_click: null
    }),

    async created() {
      var r = JSON.parse(window.sessionStorage.getItem('route'))

      console.time()
      if((typeof r === 'undefined' || r == null) || r['route_short_name'] != this.$route.params.ID.padStart(3, "0")){
        await this.fetch_route()
        window.sessionStorage.setItem('route', JSON.stringify(this.route))
        await this.fetch_trips()
        await this.fetch_shapes()
        await this.fetch_lines()
        await this.fetch_trip_notes()
        await this.fetch_stop_times()
        await this.fetch_stops()
        await this.fetch_calendar()
        window.sessionStorage.setItem('calendar_options', JSON.stringify(this.calendar_options))
        await this.fetch_calendar_dates()
        
        var trips_aux = [[], []]
        var trip_notes_aux = [[], []]
        var first_spots = [[], []]
        var second_spots = [[], []]
        var shapes_aux = [[], []]
        for(let i = 0; i < 2; i++){
          var spots = this.filter_stops(i)
          for(let j = 0; j < this.calendar_options[i].length; j++){
            var trips = this.filter_trips(j, spots, i)
            trips_aux[i].push(trips)
            var trip_notes = this.filter_trip_notes(trips)
            trip_notes_aux[i].push(trip_notes)
            var principal_spots = this.filter_principal_spots(spots, i, trips)
            first_spots[i].push(principal_spots)
            this.show_options[i].push(Array(first_spots[i].length).fill(false))
            var intermediate_spots = this.filter_intermediate_spots(spots, principal_spots, i, j, trips)
            second_spots[i].push(intermediate_spots)
            var shapes = this.filter_shapes(trips)
            shapes_aux[i].push(shapes)
            var code = this.insert_codes(trips)
            this.codes[i].push(code)
          }
        }
        window.sessionStorage.setItem('stops_by_trip', JSON.stringify(this.stops_by_trip))
        window.sessionStorage.setItem('show_options', JSON.stringify(this.show_options))
        window.sessionStorage.setItem('codes', JSON.stringify(this.codes))
        this.trips_by_direction_schedule = Object.freeze(trips_aux)
        window.sessionStorage.setItem('trips_by_direction_schedule', JSON.stringify(this.trips_by_direction_schedule))
        this.trip_notes_by_trip = Object.freeze(trip_notes_aux)
        window.sessionStorage.setItem('trip_notes_by_trip', JSON.stringify(this.trip_notes_by_trip))
        this.principal_spots_by_trip = Object.freeze(first_spots)
        window.sessionStorage.setItem('principal_spots_by_trip', JSON.stringify(this.principal_spots_by_trip))
        this.intermediate_spots_by_trip = Object.freeze(second_spots)
        window.sessionStorage.setItem('intermediate_spots_by_trip', JSON.stringify(this.intermediate_spots_by_trip))
        this.shapes_by_trip = Object.freeze(shapes_aux)
        window.sessionStorage.setItem('shapes_by_trip', JSON.stringify(this.shapes_by_trip))
      }
      else{
        this.route = r
        this.trips_by_direction_schedule = JSON.parse(window.sessionStorage.getItem('trips_by_direction_schedule'))
        this.trip_notes_by_trip = JSON.parse(window.sessionStorage.getItem('trip_notes_by_trip'))
        this.stops_by_trip = JSON.parse(window.sessionStorage.getItem('stops_by_trip'))
        this.principal_spots_by_trip = JSON.parse(window.sessionStorage.getItem('principal_spots_by_trip'))
        this.intermediate_spots_by_trip = JSON.parse(window.sessionStorage.getItem('intermediate_spots_by_trip'))      
        this.show_options = JSON.parse(window.sessionStorage.getItem('show_options'))
        this.calendar_options = JSON.parse(window.sessionStorage.getItem('calendar_options'))
        this.shapes_by_trip = JSON.parse(window.sessionStorage.getItem('shapes_by_trip'))
        this.codes = JSON.parse(window.sessionStorage.getItem('codes'))
      }
      console.timeEnd()

      console.log('FILTRAGEM FEITA')
      this.tab_first[0] = "tab-" + this.calendar_options[0].findIndex(obj => {
        return typeof obj['today'] !== 'undefined'
      })
      this.tab_first[1] = "tab-" + this.calendar_options[1].findIndex(obj => {
        return typeof obj['today'] !== 'undefined'
      })
      console.log(this.stops_by_trip[0][0].find(obj => {return obj['stop_id'] ===1 && obj['trip_id'] === 1200799}))
      this.loading = true
    },

    methods: {
      async fetch_route(){
        var aux
        await fetch("http://localhost:1337/api/routes")
          .then(response => response.json())
          .then(data => aux = data.data.map(obj => obj['attributes']))
        var route_short_name = this.$route.params.ID.padStart(3, "0")
        this.route = aux.find(obj => {
          return obj['route_short_name'] === route_short_name
        })
        //console.log(this.route)
      },

      async fetch_lines(){
        var aux
        await fetch("http://localhost:1337/api/lines")
          .then(response => response.json())
          .then(data => aux = data.data.map(obj => obj['attributes']))
        this.lines = aux.filter(obj => {
          return obj['route_id'] === this.route['route_id']
        })
        //console.log(this.lines)
      },

      async fetch_trips(){
        var aux
        await fetch("http://localhost:1337/api/trips")
          .then(response => response.json())
          .then(data => aux = data.data.map(obj => obj['attributes']))
        this.trips = aux.filter(obj => {
          return obj['route_id'] === this.route['route_id']
        })
        //console.log(this.trips)
      },

      async fetch_shapes(){
        var aux
        await fetch("http://localhost:1337/api/shapes")
          .then(response => response.json())
          .then(data => aux = data.data.map(obj => obj['attributes']))
        var route_short_name = this.$route.params.ID
        this.shapes = aux.filter(obj => {
          return obj['shape_id'].split("_")[0] === route_short_name
        })
        //console.log(this.trips)
      },

      async fetch_trip_notes(){
        var aux
        await fetch("http://localhost:1337/api/trip-notes")
          .then(response => response.json())
          .then(data => aux = data.data.map(obj => obj['attributes']))
        var trips_ids = this.trips.map(obj => obj['trip_id'])
        this.trip_notes = aux.filter(obj => {
          return trips_ids.includes(obj['trip_id'])
        })
        //console.log(this.trip_notes)
      },

      async fetch_stop_times(){
        var aux
        await fetch("http://localhost:1337/api/stop-times")
          .then(response => response.json())
          .then(data => aux = data.data.map(obj => obj['attributes']))
        var trips_ids = this.trips.map(obj => obj['trip_id'])
        this.stop_times = aux.filter(obj => {
          return trips_ids.includes(obj['trip_id'])
        })
        //console.log(this.stop_times)
      },

      async fetch_stops(){
        var aux
        await fetch("http://localhost:1337/api/stops")
          .then(response => response.json())
          .then(data => aux = data.data.map(obj => obj['attributes']))
        var stops_ids = this.stop_times.map(obj => obj['stop_id'])
        this.stops = aux.filter(obj => {
          return stops_ids.includes(obj['stop_id'])
        })
        //console.log(this.stops)
      },

      async fetch_calendar(){
        var aux
        await fetch("http://localhost:1337/api/calendars")
          .then(response => response.json())
          .then(data => aux = data.data.map(obj => obj['attributes']))
        
        var services_front = this.trips.filter(obj => {
          return obj['direction_id'] == '1'
        })
        var services_ids_front = services_front.map(obj => obj['service_id'])
        var services_back = this.trips.filter(obj => {
          return obj['direction_id'] == '0'
        })
        var services_ids_back = services_back.map(obj => obj['service_id'])

        this.calendar = aux.filter(obj => {
          return services_ids_front.includes(obj['service_id']) || services_ids_back.includes(obj['service_id'])
        })

        for(let i = 0; i < this.calendar.length; i++){
          var obj
          if(services_ids_front.includes(this.calendar[i]['service_id']))           
            obj = this.fill_schedules(1, this.calendar[i])
          if(services_ids_back.includes(this.calendar[i]['service_id']))
            obj = this.fill_schedules(0, this.calendar[i])

          Vue.set(this.calendar, i, obj)
        }
        //console.log(this.calendar)
      },

      async fetch_calendar_dates(){
        var aux
        await fetch("http://localhost:1337/api/calendar-dates")
          .then(response => response.json())
          .then(data => aux = data.data.map(obj => obj['attributes']))
        var service_ids = this.calendar.map(obj => obj['service_id'])
        this.calendar_dates = aux.filter(obj => {
          return service_ids.includes(obj['service_id'])
        })
      },

      fill_schedules(direction, aux_calendar_obj){
        var calendar_obj = aux_calendar_obj
        var actual_date = new Date()
        var day = actual_date.getDay();
        var obj = {}
        if(calendar_obj['monday'] == 1 && calendar_obj['tuesday'] == 1 && calendar_obj['wednesday'] == 1 && calendar_obj['thursday'] == 1 && calendar_obj['friday'] == 1){
          obj['type'] = 'Dias úteis'
          if(day >= 1 && day <= 5)
            obj['today'] = true
          this.calendar_options[direction].push(obj)
          calendar_obj['type'] = 'Dias úteis'
        }
        else if(calendar_obj['monday'] == 1 && calendar_obj['tuesday'] == 1 && calendar_obj['wednesday'] == 1 && calendar_obj['thursday'] == 1){
          obj['type'] = 'Segundas, terças, quartas e quintas'
          if(day >= 1 && day <= 4)
            obj['today'] = true
          this.calendar_options[direction].push(obj)
          calendar_obj['type'] = 'Segundas, terças, quartas e quintas'
        }
        else if( calendar_obj['friday'] == 1){
          obj['type'] = 'Sextas'
          if(day == 5)
            obj['today'] = true
          this.calendar_options[direction].push(obj)
          calendar_obj['type'] = 'Sextas'
        }
        else if(calendar_obj['saturday'] == 1 && calendar_obj['sunday'] != 1){
          obj['type'] = 'Sábados'
          if(day == 6)
            obj['today'] = true
          this.calendar_options[direction].push(obj)
          calendar_obj['type'] = 'Sábados'
        }
        else if(calendar_obj['saturday'] == 1 && calendar_obj['sunday'] == 1){
          obj['type'] = 'Sábados, domingos e feriados'
          if(day == 6 || day == 0)
            obj['today'] = true
          this.calendar_options[direction].push(obj)
          calendar_obj['type'] = 'Sábados, domingos e feriados'
        }
        else if(calendar_obj['sunday'] == 1){
          obj['type'] = 'Domingos e feriados'
          if(day == 0)
            obj['today'] = true
          this.calendar_options[direction].push(obj)
          calendar_obj['type'] = 'Domingos e feriados'
        }
        else{
          obj['type'] = 'Quartas'
          if(day == 5 || day == 3)
            obj['today'] = true
          this.calendar_options[direction].push(obj)
          calendar_obj['type'] = 'Quartas'
        }
        return calendar_obj
      },

      filter_trips(i, stops, direction){
        var service = this.calendar.find(obj =>{
          return obj['type'] === this.calendar_options[direction][i]['type']
        })
        var trips = this.trips.filter(obj => {
          return  obj['direction_id'] === direction && obj['service_id'] === service['service_id']
        })
        var aux = []
        for(let ind = 0; ind < trips.length; ind++){
          var stops_by_trip = stops.filter(obj => {
            return obj['trip_id'] === trips[ind]['trip_id']
          })
          aux.push(stops_by_trip)
        }
        var first_spots = []  
        var last_stops = []  
        for(let indx = 0; indx < aux.length; indx++){
          first_spots.push(aux[indx][0])
          last_stops.push(aux[indx][aux[indx].length-1])
        }
        first_spots.sort((a,b) =>  a['departure_time'].localeCompare(b['departure_time']))
        
        var trips_ordered = first_spots.map(obj => obj['trip_id'])

        var last_spots_ordered = last_stops.sort(function (a,b){
          var A = a['trip_id'], B = b['trip_id']
          if (trips_ordered.indexOf(A) > trips_ordered.indexOf(B)) 
            return 1
          else 
            return -1
        })

        var ts = trips.sort( function (a, b) {
          var A = a['trip_id'], B = b['trip_id'];  
          if (trips_ordered.indexOf(A) > trips_ordered.indexOf(B)) 
            return 1
          else 
            return -1
        })

        for(let ind = 0; ind < ts.length; ind++){
          ts[ind]['first_spot'] = first_spots[ind]['stop_name']
          ts[ind]['last_spot'] = last_spots_ordered[ind]['stop_name']
        }
        return ts
      },

      filter_shapes(trips){
        var shapes_ids = trips.map(obj => obj['shape_id'])
        var shapes = this.shapes.filter(obj => {
          return shapes_ids.includes(obj['shape_id'])
        })
        var ss = shapes.sort(function (a,b){
          var A = a['shape_id'], B = b['shape_id'];  
            if (shapes_ids.indexOf(A) > shapes_ids.indexOf(B)) {
              return 1;
            } else {
              return -1;
            }
        })
        return ss
      },

      filter_trip_notes(trips){
        var trips_ids = trips.map(obj => obj['trip_id'])
        var trips_notes = this.trip_notes.filter(obj => {
          return trips_ids.includes(obj['trip_id'])
        })
        var j = 0
        var tn = []
        if(trips_notes.length > 0){
          for(let i = 0; i < trips_ids.length; i++){
            if(j != trips_notes.length && trips_notes[j]['trip_id'] == trips_ids[i]){
              trips_notes[j]['M_index'] = i + 1
              tn.push(trips_notes[j])
              j++
            }
          }
        }
        return tn
      },

      filter_stops(direction){
        var trips = this.trips.filter(obj => {
          return obj['direction_id'] === direction
        })
        var trips_ids = trips.map(obj => obj['trip_id'])

        var spots = this.stop_times.filter(obj => {
          return trips_ids.includes(obj['trip_id'])
        })
        var spots_ids = spots.map(obj => obj['stop_id'])

        var spots_by_line = this.lines.filter(obj => {
          return spots_ids.includes(obj['stop_id']) && obj['direction_id'] === direction
        })

        for(let i = 0; i < spots.length; i++){
          var aux_obj = spots_by_line.find(obj => {
            return obj['stop_id'] === spots[i]['stop_id']
          })
          spots[i]['sequence'] = aux_obj['sequence']
          var stop = this.stops.find(obj => {
            return obj['stop_id'] === spots[i]['stop_id']
          })
          spots[i]['stop_name'] = stop['stop_name']
          spots[i]['stop_lon'] = stop['stop_lon']
          spots[i]['stop_lat'] = stop['stop_lat']
        }
        spots.sort((a,b) =>  parseFloat(a['sequence']) - parseFloat(b['sequence']))

        return spots
      },

      filter_principal_spots(stops, direction, trips){
        var trips_ids = trips.map(obj => obj['trip_id'])

        var principal_spots_aux = stops.filter(obj => {
          return obj['timepoint'] === 1 && trips_ids.includes(obj['trip_id'])
        })

        this.stops_by_trip[direction].push(principal_spots_aux)

        var principal_spots = principal_spots_aux.filter((value, index, self) => 
          index === self.findIndex((obj) => (
            obj['stop_id'] === value['stop_id']
          ))
        )
        return principal_spots
      },

      filter_intermediate_spots(spots, principal_spots, direction, i, trips){
        var trips_ids = trips.map(obj => obj['trip_id'])
        var principal_spots_ids = principal_spots.map(obj => obj['stop_id'])

        var intermediate_spots_aux = spots.filter(obj => {
          return principal_spots_ids.includes(obj['stop_id']) === false && trips_ids.includes(obj['trip_id'])
        })

        var aux = this.stops_by_trip[direction][i]
        Vue.set(this.stops_by_trip[direction], i, aux.concat(intermediate_spots_aux))

        var intermediate_spots = intermediate_spots_aux.filter((value, index, self) => 
          index === self.findIndex((obj) => (
            obj['stop_id'] === value['stop_id']
          ))
        )

        var intermediate_list = []
        for(let j = 0; j < principal_spots.length-1; j++){
          var intermediates_between = intermediate_spots.filter(obj =>{
            return obj['sequence'] > principal_spots[j]['sequence'] && obj['sequence'] < principal_spots[j+1]['sequence']
          })
          intermediate_list.push(intermediates_between)
        }

        return intermediate_list
      },

      get_color(stop){
        if(stop['timepoint'] == 1)
          return 'black--text'
        else
          return 'grey--text'
      },

      get_stop_times(trips, stops, stop){
        var sts = []
        for(let i = 0; i < trips.length; i++){
          var st = stops.find(obj => {
            return obj['trip_id'] === trips[i]['trip_id'] && obj['stop_id'] === stop['stop_id']
          })
          if(st == null || typeof st === 'undefined')
            sts.push({ "departure_time": '-', "color":'grey--text'})
          else{
            st['color'] = this.get_color(st)
            if(st['stop_name'] === trips[i]['first_spot'])
              st['icon_1'] = 'mdi-alpha-p-circle'
            else if(st['stop_name'] === trips[i]['last_spot'])
              st['icon_2'] = 'mdi-alpha-c-circle'
            sts.push(st)
          }
        }
        return sts
      },

      insert_codes(trips){
        var aux_codes = []
        for(let i = 0; i < trips.length; i++)
          aux_codes.push('M' + (i+1))
        return aux_codes
      },

      show_intermediates(i, direction, stop_index){
        var aux_array = this.show_options[direction]
        aux_array[i][stop_index] = !aux_array[i][stop_index]
        Vue.set(this.show_options, direction, aux_array)
      },

      change_direction(){
        if(this.direction == 1)
          this.direction = 0
        else  
          this.direction = 1
      },

      handle(stops, stop){
        console.log(stop)
        var stop_obj = stops.find(x => x.stop_id === stop)
        console.log(stop_obj)
        this.stop_click = { lat: parseFloat(stop_obj.stop_lat), lng: parseFloat(stop_obj.stop_lon), stop_id: stop }
        console.log(this.stop_click)
        
        window.scrollTo( { top: document.body.scrollHeight || document.documentElement.scrollHeight, behavior: "smooth" });
      },
    },
  }
</script>

<style>

/* Background header */
.header{
  background: #d9ecf2 url('https://tub.pt/templates/frontoffice/home/img/icone1.svg') no-repeat center center !important;
  background-size: 100px 100px !important;
  border-radius: 5px !important;
  height: 120px;
}

/* Change background's color text */
.text_color{
  background-color: #007DAB !important;
}


/* Force elemtents to be separated with a paragraph (specifically, in the button on the right side of the header) */
.vertical_button{
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: flex-start !important;
}

.hidden_icon{
  position: inherit !important;
}

.reference_color{
  color: #007DAB;
}

/* TABLE DETAILS */
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  padding: 8px;
  text-align: center;
}

.header_column{
  position: absolute;
  display: flex !important; 
  align-items: center !important;
  justify-content: center !important; 
  text-align: center !important; 
  background-color: #D9ECF2;
  color: #007DAB;
  width: 300px;
  height: 70px;
}

.header_column:hover {
  background-color: #cedce7;
  color: rgb(0, 81, 255);
}

.intermediate_column{
  position: absolute;
  display: flex !important; 
  align-items: center !important;
  justify-content: center !important; 
  text-align: center !important; 
  background: white;
  color: #007DAB;
  width: 300px;
  height: 70px;
}

.button_column{
  position: absolute;
  display: flex !important; 
  align-items: center !important;
  justify-content: center !important; 
  text-align: center !important; 
  background: white;
  color: #007DAB;
  width: 300px;
  height: 40px;
}

.code_column{
  position: absolute;
  display: flex !important; 
  align-items: center !important;
  justify-content: center !important; 
  text-align: center !important; 
  background: #007DAB;
  color: white;
  width: 300px;
  height: 60px;
}

tr:nth-child(odd)  {
  background-color: #D9ECF2;
}

.color_row{
  background-color: white!important;
  height: 70px;
}

.code_row{
  background-color: #007DAB;
  height: 60px;
}

.button_row{
  height: 40px;
}

.principal_row{
  height: 70px;
}

.table_specs{
  overflow-x: auto;
  overflow-y: hidden;
}


</style>