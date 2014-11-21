angular.module('LabsterBackOffice')

  .factory('LicenseService', function () {
    return({
      checkVatFormat: checkVatFormat,
      checkInstitution: checkInstitution,
      getEuCountries: getEuCountries,
      checkEuCountry: checkEuCountry
    });

    function checkVatFormat(vat_number) {
      if (!vat_number.length) {
        return "Please insert your VAT number";
      } else if (checkVATNumber(vat_number)) {
        // validated
        return "";
      } else {
        return "The VAT number is invalid";
      }
    }

    function checkInstitution(institution_name) {
      if (!institution_name.length) {
        return "Please insert your school/university name";
      } else {
        return "";
      }
    }

    function getEuCountries() {
      return [
        {id: 15, name: 'Austria'},
        {id: 22, name: 'Belgium'},
        {id: 35, name: 'Bulgaria'},
        {id: 56, name: 'Croatia'},
        {id: 59, name: 'Cyprus'},
        {id: 60, name: 'Czech Republic'},
        {id: 61, name: 'Denmark'},
        {id: 70, name: 'Estonia'},
        {id: 75, name: 'Finland'},
        {id: 76, name: 'France'},
        {id: 83, name: 'Germany'},
        {id: 86, name: 'Greece'},
        {id: 101, name: 'Hungary'},
        {id: 107, name: 'Ireland'},
        {id: 110, name: 'Italy'},
        {id: 123, name: 'Latvia'},
        {id: 129, name: 'Lithuania'},
        {id: 130, name: 'Luxembourg'},
        {id: 138, name: 'Malta'},
        {id: 157, name: 'Netherlands'},
        {id: 177, name: 'Poland'},
        {id: 178, name: 'Portugal'},
        {id: 182, name: 'Romania'},
        {id: 202, name: 'Slovakia'},
        {id: 203, name: 'Slovenia'},
        {id: 208, name: 'Spain'},
        {id: 214, name: 'Sweden'},
        {id: 234, name: 'United Kingdom'},
      ];
    }

    function checkEuCountry(country) {
      var eu_countries = getEuCountries();
      if (country != null || country != undefined) {
        for (var i = eu_countries.length - 1; i >= 0; i--) {
          var item = eu_countries[i];
          if (item.id == country.id) {
            return true;
          }
        }
      }
      return false;
    }
  });