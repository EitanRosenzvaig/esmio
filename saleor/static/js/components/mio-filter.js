import React from 'react';
import ReactDOM from 'react-dom';

import MioFilter from './mioFilter/MioFilter';


export default $(document).ready((e) => {

  const mioFilterContainer = document.getElementById('mio-filter');

  if (mioFilterContainer) {
    ReactDOM.render(
      <MioFilter
        url={mioFilterContainer.dataset.url}
      />,
      mioFilterContainer
    );
  }

});
