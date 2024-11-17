import axios from 'axios';
import { DegreeWizardPayload } from 'types/degreeWizard';
import { withAuthorization } from './authApi';

export const setupDegreeWizard = async (token: string, wizard: DegreeWizardPayload) => {
  try {
    await axios.post('/user/setupDegreeWizard', wizard, {
      headers: withAuthorization(token)
    });
  } catch (err) {
    console.error('Error resetting degree at setupDegreeWizard: ', err);
    throw err;
  }
};
