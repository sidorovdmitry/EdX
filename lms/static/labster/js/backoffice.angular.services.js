angular.module('LabsterBackOffice')

  .factory('LicenseService', function () {
    var eu_countries = [
      {id: 15, alpha2: "AT", name: "Austria"},
      {id: 22, alpha2: "BE", name: "Belgium"},
      {id: 35, alpha2: "BG", name: "Bulgaria"},
      {id: 56, alpha2: "HR", name: "Croatia"},
      {id: 59, alpha2: "CY", name: "Cyprus"},
      {id: 60, alpha2: "CZ", name: "Czech Republic"},
      {id: 61, alpha2: "DK", name: "Denmark"},
      {id: 70, alpha2: "EE", name: "Estonia"},
      {id: 75, alpha2: "FI", name: "Finland"},
      {id: 76, alpha2: "FR", name: "France"},
      {id: 83, alpha2: "DE", name: "Germany"},
      {id: 86, alpha2: "GR", name: "Greece"},
      {id: 101, alpha2: "HU", name: "Hungary"},
      {id: 107, alpha2: "IE", name: "Ireland"},
      {id: 110, alpha2: "IT", name: "Italy"},
      {id: 123, alpha2: "LV", name: "Latvia"},
      {id: 129, alpha2: "LT", name: "Lithuania"},
      {id: 130, alpha2: "LU", name: "Luxembourg"},
      {id: 138, alpha2: "MT", name: "Malta"},
      {id: 157, alpha2: "NL", name: "Netherlands"},
      {id: 177, alpha2: "PL", name: "Poland"},
      {id: 178, alpha2: "PT", name: "Portugal"},
      {id: 182, alpha2: "RO", name: "Romania"},
      {id: 202, alpha2: "SK", name: "Slovakia"},
      {id: 203, alpha2: "SI", name: "Slovenia"},
      {id: 208, alpha2: "ES", name: "Spain"},
      {id: 214, alpha2: "SE", name: "Sweden"},
      {id: 234, alpha2: "GB", name: "United Kingdom"},
    ];

    return({
      checkVatFormat: checkVatFormat,
      checkInstitution: checkInstitution,
      checkEuCountry: checkEuCountry,
      getIndexCountry: getIndexCountry,
      getIndexCountryByCode: getIndexCountryByCode
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

    function checkEuCountry(country) {
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

    function getIndexCountry(countryId, all_countries) {
      for (var i = 0; i < all_countries.length; i++) {
        if (all_countries[i].id == countryId) {
          return i;
        }
      }
      return 0;
    }

    function getIndexCountryByCode(countryCode, all_countries) {
      for (var i = 0; i < all_countries.length; i++) {
        if (all_countries[i].alpha2 == countryCode) {
          return i;
        }
      }
      return 0;
    }
  });