import axios from 'axios';
import { Specialisations, SpecialisationTypes } from 'types/api';

export const getSpecialisationsForProgram = async (
  programCode: string,
  specType: string
): Promise<Specialisations> => {
  const res = await axios.get<Specialisations>(
    `/specialisations/getSpecialisations/${programCode}/${specType}`
  );

  return res.data;
};

export const getSpecialisationTypes = async (programCode: string): Promise<SpecialisationTypes> => {
  const res = await axios.get<SpecialisationTypes>(
    `/specialisations/getSpecialisationTypes/${programCode}`
  );

  return res.data;
};
