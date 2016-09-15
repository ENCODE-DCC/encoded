'use strict';

var SingleTreatment = module.exports.SingleTreatment = function(treatment) {
    var treatmentText = '';

    if (treatment.amount) {
        treatmentText += treatment.amount + (treatment.amount_units ? ' ' + treatment.amount_units : '') + ' ';
    }
    treatmentText += treatment.treatment_term_name + (treatment.treatment_term_id ? ' (' + treatment.treatment_term_id + ')' : '') + ' ';
    if (treatment.duration) {
        treatmentText += 'for ' + treatment.duration + ' ' + (treatment.duration_units ? treatment.duration_units : '');
    }
    return treatmentText;
};
