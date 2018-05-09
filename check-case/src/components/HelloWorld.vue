<template>
  <div>
    <div class="md-layout md-gutter md-alignment-center-center">
      <div class="md-layout-item md-size-60">
        <form novalidate class="md-layout" @submit.prevent="validateForm">
          <md-field :class="getValidationClass('caseNumber')">
            <label>Case Number:</label>
            <md-input v-model="form.caseNumber"></md-input>
            <span class="md-helper-text">USCIS case number.</span>
            <span class="md-error" v-if="!$v.form.caseNumber.required">The age is required</span>
            <span class="md-error" v-else-if="!$v.form.caseNumber.maxlength">Invalid age</span>
            <span class="md-error" v-else-if="!$v.form.caseNumber.minlength">Invalid age</span>
          </md-field>
          <md-field :class="getValidationClass('email')">
            <label>Email:</label>
            <md-input v-model="form.email"></md-input>
            <span class="md-error" v-if="!$v.form.email.required">The email is required</span>
            <span class="md-error" v-else-if="!$v.form.email.email">Invalid email</span>
            <span class="md-helper-text">The email address to receive the notice.</span>
          </md-field>
          <md-button type="submit" class="md-dense md-raised md-primary">Submit</md-button>
        </form>
      </div>
    </div>
    <div class="md-layout md-gutter md-alignment-center-center">
      <div class="md-layout-item md-size-25">
        <pie-chart :data="status_distribution"></pie-chart>
        <div>Status</div>
      </div>
      <div class="md-layout-item md-size-25">
        <pie-chart :data="interval_distribution"></pie-chart>
        <div>Check intervals</div>
      </div>
    </div>
    <div class="md-layout md-gutter md-alignment-center-center">
    </div>
    <pre>{{ $v.errors }} {{$v.status_distribution}}</pre>
  </div>
</template>

<script>
import axios from 'axios';
import { validationMixin } from 'vuelidate'
import {
  required,
  email,
  minLength,
  maxLength
} from 'vuelidate/lib/validators'

export default {
  mixins: [validationMixin],
  data() {
    return {
      form: {
        caseNumber: null,
        email: null,
      },
      errors: [],
      status_distribution: [],
      interval_distribution: []
    }
  },
  validations: {
    form: {
      caseNumber: {
        required,
        minLength: minLength(13),
        maxLength: maxLength(13)
      },
      email: {
        required,
        email
      }
    }
  },
  mounted() {
    axios.get('/api/status').then(response => {
      response.data.status_distribution.forEach(item => {
        this.status_distribution.push([item.status, item.cnt]);
      });
      response.data.interval_distribution.forEach(item => {
        console.log(this);
        this.interval_distribution.push([item.interval, item.cnt]);
      });
      console.log(response);
    }).catch(e => {
      console.log(e);
    })
  },
  methods: {
    getValidationClass (fieldName) {
      const field = this.$v.form[fieldName];
      if (field) {
        return {
          'md-invalid': field.$invalid && field.$dirty
        }
      }
    },
    validateForm () {
      this.$v.$touch();
      if (!this.$v.$invalid) {
        axios.post('/api/cases', {
          case_id: this.form.caseNumber,
          email: this.form.email
        })
        .then(response => {
          console.log(response);
        })
        .catch(e => {
          console.log(e);
        })
      }
    }
  }
}
</script>
