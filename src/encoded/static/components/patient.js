import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { RelatedItems } from './item';
import { DisplayAsJson } from './objectutils';
import formatMeasurement from './../libs/formatMeasurement';
import { CartToggle } from './cart';
import Status from './status';
import MedicationChart from './medicationChart';
import GermlineTable from './germlineTable';
import IHCTable from './ihcTable';

import PatientChart from "./patientChart";
import Radiation from "./radiation";
import CollapsiblePanel from './collapsiblePanel';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAngleDoubleUp } from "@fortawesome/free-solid-svg-icons";
import SurgeryChart from './surgeryChart';
import BiospecimenTable from "./biospecimenTable";
import PatientPathTable from './patientPathTable';

/* eslint-disable react/prefer-stateless-function */
class Patient extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showButton: false
    }
    this.topFunction = this.topFunction.bind(this);
    this.listenToScroll = this.listenToScroll.bind(this);
  }

  topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
  }

  listenToScroll() {
    let mybutton = document.getElementById("scrollUpButton");
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
      mybutton.style.display = "block";
    } else {
      mybutton.style.display = "none";
    }

  }

  componentDidMount() {
    window.addEventListener('scroll', this.listenToScroll)
  }

  componentWillUnmount() {
    window.removeEventListener('scroll', this.listenToScroll)
  }

  createPathPanel() {
    let list = [];
    let surgeryData = this.props.context.surgery;
    if (surgeryData.length > 1) {
      surgeryData.sort((a, b) => Date.parse(a.date) - Date.parse(b.date));
    }
    for (let i = 0; i < surgeryData.length; i++) {
      list.push(<div data-test="surgery"><dt>Surgery Date</dt><dd>{surgeryData[i].date}</dd> </div>)
      if (surgeryData[i].pathology_report && surgeryData[i].pathology_report.length > 0) {
        for (let j = 0; j < surgeryData[i].pathology_report.length; j++) {
          list.push(<div data-test="surgery.pathology_report"><dt>pathology_report</dt><dd><a href={surgeryData[i].pathology_report[j]['@id']}>{surgeryData[i].pathology_report[j].accession}</a></dd> </div>)
          list.push(<div data-test="surgery.pathology_report"><dt>Histologic Subtype</dt><dd>{surgeryData[i].pathology_report[j].histology}</dd> </div>)
          list.push(<div data-test="surgery.pathology_report"><dt>pT stage</dt><dd>{surgeryData[i].pathology_report[j].t_stage}</dd> </div>)
          list.push(<div data-test="surgery.pathology_report"><dt>pN stage</dt><dd>{surgeryData[i].pathology_report[j].n_stage}</dd> </div>)
          list.push(<div data-test="surgery.pathology_report"><dt>pM stage</dt><dd>{surgeryData[i].pathology_report[j].m_stage}</dd> </div>)
        }
      }
      if (i != surgeryData.length - 1) {
        list.push(<div className="row" style={{ borderTop: "1px solid #151313" }}></div>)
      }


    }
    return list

  }
  render() {

    const context = this.props.context;
    const itemClass = globals.itemClass(context, 'view-item');
    // Set up breadcrumbs
    const crumbs = [
      { id: 'Patients' },
      { id: <i>{context.accession}</i> },
    ];
    const crumbsReleased = (context.status === 'released');
    let hasLabs = false;
    let hasVitals = false;
    let hasPath = false;
    let hasSurgery = false;
    let hasIHC = false;
    let hasMedication = false;
    let hasRadiation = false;
    let hasBiospecimen = false;
    if (Object.keys(this.props.context.labs).length > 0) {
      hasLabs = true;
    }
    if (Object.keys(this.props.context.vitals).length > 0) {
      hasVitals = true;
    }
    if (Object.keys(this.props.context.surgery).length > 0) {
      hasPath = true;
    }
    if (Object.keys(this.props.context.surgery).length > 0) {
      hasSurgery = true;
    }
    if (Object.keys(this.props.context.ihc).length > 0) {
      hasIHC = true;
    }
    if (Object.keys(this.props.context.medications).length > 0) {
      hasMedication = true;
    }
    if (Object.keys(this.props.context.radiation).length > 0) {
      hasRadiation = true;
    }
    if (Object.keys(this.props.context.biospecimen).length > 0) {
      hasBiospecimen = true;
    }
    const labsPanelBody = (
      <PatientChart chartId="labsChart" data={context.labs} ></PatientChart>

    );
    const vitalsPanelBody = (
      <PatientChart chartId="vitalChart" data={context.vitals} ></PatientChart>
    );
    const surgeryPanelBody = (
      <SurgeryChart chartId="surgery" data={context.surgery} chartTitle="Surgeries Results Over Time"></SurgeryChart>
    );

    const medicationPanelBody = (
      <MedicationChart chartId="medication" data={context.medications} chartTitle="Medications Results Over Time"></MedicationChart>
    );
    const radiationPanelBody = (
      <Radiation chartId="radiation" data={context.radiation} chartTitle="Radiation History"></Radiation>
    );
    const pathPanelBody = (
      <dl className="key-value">{this.createPathPanel()}</dl>
    );


    return (
      <div className={globals.itemClass(context, 'view-item')}>
        <header className="row">
          <script src="https://cdn.plot.ly/plotly-1.51.3.min.js"></script>
          <script src="https://unpkg.com/axios@0.18.0/dist/axios.min.js" ></script>
          <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.24.0/moment.min.js" ></script>
          <div className="col-sm-12">
            <Breadcrumbs root="/search/?type=Patient" crumbs={crumbs} crumbsReleased={crumbsReleased} />
            <h2>{context.accession}</h2>
            <div className="cart__toggle--header">
                <CartToggle element={context} />
            </div>
          </div>
        </header>

        <Panel>
          <PanelHeading>
            <h4>Patient Information</h4>
          </PanelHeading>
          <PanelBody>
            <dl className="key-value">
              <div data-test="status">
                <dt>Status</dt>
                <dd><Status item={context} inline /></dd>
              </div>
              <div data-test="gender">
                <dt>Gender</dt>
                <dd>{context.gender}</dd>
              </div>

              <div data-test="ethnicity">
                <dt>Ethnicity</dt>
                <dd>{context.ethnicity}</dd>
              </div>

              <div data-test="race">
                <dt>Race</dt>
                <dd>{context.race}</dd>
              </div>

              <div data-test="age">
                <dt>Age at diagnosis</dt>
                <dd className="sentence-case">
                  {formatMeasurement(context.age, context.age_units)}
                </dd>
              </div>
              {context.death_date && <div data-test="death_date">
                <dt>Death Date</dt>
                <dd>{`${context.death_date} ( Death source: `}{`${context.death_source} )`}</dd>
              </div>}
            </dl>
          </PanelBody>
        </Panel>
        {hasLabs && <CollapsiblePanel panelId="myPanelId1" title="Lab Results Over Time" content={labsPanelBody} />}
        {hasVitals && <CollapsiblePanel panelId="myPanelId2" title="Vital Results Over Time" content={vitalsPanelBody} />}
        {hasPath && <PatientPathTable data={context.surgery} tableTitle="Patient Diagnosis"></PatientPathTable>}
        {hasSurgery && <CollapsiblePanel panelId="myPanelId3" title="Surgical Results Over Time" content={surgeryPanelBody} />}
        {hasIHC && <IHCTable data={context.ihc} tableTitle="IHC Assay Staining Results"></IHCTable>}
        {hasMedication && <CollapsiblePanel panelId="myPanelId4" title="Medications Results Over Time" content={medicationPanelBody} />}
        {<GermlineTable data={context.germline} tableTitle="Germline Mutation"></GermlineTable>}
        {hasRadiation && <CollapsiblePanel panelId="myPanelId5" title="Radiation History" content={radiationPanelBody} />}
        {hasBiospecimen && <BiospecimenTable data={context.biospecimen} tableTitle="Biospecimens from this patient"></BiospecimenTable>}
        <button onClick={this.topFunction} id="scrollUpButton" title="Go to top"><FontAwesomeIcon icon={faAngleDoubleUp} size="2x" /></button>
      </div>
    );
  }
}
/* eslint-enable react/prefer-stateless-function */

Patient.propTypes = {
  context: PropTypes.object, // Target object to display
};

Patient.defaultProps = {
  context: null,
};

globals.contentViews.register(Patient, 'Patient');

