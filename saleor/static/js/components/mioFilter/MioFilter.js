import _ from 'lodash';
import $ from 'jquery';
import classNames from 'classnames';
import { observer } from 'mobx-react';
import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom'

import * as queryString from 'query-string';

export default observer(class MioFilter extends Component {
  static propTypes = {
    url: PropTypes.string.isRequired,
  };

  constructor (props) {
    super(props);
    const { url } = this.props;

    this.state = {
      errors: {},
    };
  }

  showCards = () => {
    $('.hidden').show();
  };

  showProductLists = () => {
    $('.product-list').show();
  };

  hideProductLists = () => {
    $('.product-list').hide();
  };

  applyMioFilter = () => {
    const { url } = this.props;
    this.hideProductLists();
    this.showCards();
    // $.ajax({
    //   url: url,
    //   method: 'post',
    //   success: () => {
    //     this.openProductAtVendor();
    //   },
    //   error: (response) => {
    //     console.log(response);
    //   }
    // });
  };

  render () {
    return (
      <div>
         <button 
          onClick={this.applyMioFilter}
          className="btn btn-primary btn-lg btn-block"
          dataToggle="tooltip-filter"
          title="Aplica tu filtro personalizado.">
          <i className="fas fa-magic"></i> &nbsp;Filtro Mio!
         </button>
      </div>
    );
  }
});
