<template>
  <div style="width: 95%;">
    <md-dialog-alert
      :md-active.sync="show_dialog"
      :md-content="message"
      md-confirm-text="Cool!" />

    <div class="md-layout md-gutter md-alignment-center-center">
      <div class="md-layout-item md-size-60">
        <h3>输入case number和email,提交后系统默认每天查询一次，如果发现状态改变会发邮件通知.Good luck!</h3>
      </div>
    </div>
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
      <div class="md-layout-item md-size-60">
        <h3>数据分布：不同状态case数量以及本站每个case的查询间隔。</h3>
      </div>
    </div>
    <div class="md-layout md-gutter md-alignment-center-center">
      <div class="md-layout-item md-size-25 md-small-size-100 md-xsmall-size-100">
        <pie-chart :data="status_distribution"></pie-chart>
        <div>状态分布</div>
      </div>
      <div class="md-layout-item md-size-20 md-small-size-100 md-xsmall-size-100">
        <img src="../assets/zanshang.jpg" />
        <div>微信打赏</div>
      </div>
      <div class="md-layout-item md-size-25 md-small-size-100 md-xsmall-size-100">
        <pie-chart :data="interval_distribution"></pie-chart>
        <div>查询间隔分布(秒)</div>
      </div>
    </div>
    <div class="md-layout md-gutter md-alignment-center-center">
      <div class="md-layout-item md-size-60">
        <h3>输入case number查看该case的最近15条查询时间记录</h3>
      </div>
    </div>
    <div class="md-layout md-gutter md-alignment-center-center">
      <div class="md-layout-item md-size-60">
        <form novalidate class="md-layout" @submit.prevent="checkCaseHistoy">
          <md-field>
            <label>Case Number:</label>
            <md-input v-model="history.caseNumber"></md-input>
            <span class="md-helper-text">USCIS case number.</span>
          </md-field>
          <md-button type="submit" class="md-dense md-raised md-primary">Submit</md-button>
        </form>
      </div>
    </div>
    <div class="md-layout md-gutter md-alignment-center-center">
      <div class="md-layout-item md-size-60">
        <md-table v-if="check_history.case">
          <md-table-toolbar>
            <h1 class="md-title">Check History for Case: {{check_history.case.case_id}}</h1>
          </md-table-toolbar>
          <md-table-row>
             <md-table-head>Status</md-table-head>
             <md-table-head>Last Check Time</md-table-head>
          </md-table-row>
          <md-table-row v-for="item in check_history.case_history"
                        v-bind:key="item.id">
            <md-table-cell md-numeric>{{item.status}}</md-table-cell>
            <md-table-cell md-numeric>{{item.last_check}}</md-table-cell>
          </md-table-row>
        </md-table>
        <div v-if="!check_history.case">Wrong case number!</div>
      </div>
    </div>
    <div class="md-layout md-gutter md-alignment-center-center">
      <div class="md-layout-item md-size-60">
        <h3>站长今年也在抽h1b,懒得每天自己查询，遂写了脚本定时查询。想着和我同样情况的兄弟姐妹不在少数，就又写了个网站，方便大家使用，为了防止爬虫被禁，所以默认查询间隔为24小时。欢迎微信打赏，金额不限，打赏后扫描下方二维码联系站长，手动缩短查询时间间隔。不打赏也欢迎加站长微信，可以拉到今年微信群。打赏金用来支付服务器租赁费用。</h3>
        <img src="../assets/weixin.jpg" />
      </div>
    </div>
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
      history: {
        caseNumber: null,
      },
      errors: [],
      status_distribution: [],
      interval_distribution: [],
      check_history: {
        case: {
          case_id: ''
        }
      },
      message: '',
      show_dialog: false
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
          this.message = 'Insert Successfully!!';
          this.show_dialog = true;
        })
        .catch(e => {
          console.log(e);
          this.message = 'Error!!';
          this.show_dialog = true;
        })
      }
    },
    checkCaseHistoy () {
      axios.get('/api/cases/'+this.history.caseNumber)
      .then(response => {
        this.check_history = response.data;
      })
      .catch(e => {
        this.check_history = e;
      })
    }
  }
}
</script>

<style>
p .info: {
  font-size: 24px;
}
</style>
