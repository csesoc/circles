import axios from 'axios';
import { GraphPayload, Programs, Structure } from 'types/api';

export const getProgramGraph = async (
  programCode: string,
  specs: string[]
): Promise<GraphPayload> => {
  const res = await axios.get(`/programs/graph/${programCode}/${specs.join('+')}`);
  return res.data as GraphPayload;
};

export const getProgramStructure = async (
  programCode: string,
  specs: string[]
): Promise<Structure> => {
  const res = await axios.get<Structure>(
    `/programs/getStructure/${programCode}/${specs.join('+')}`
  );

  return res.data;
};

export const fetchAllDegrees = async (): Promise<Programs> => {
  const res = await axios.get<Programs>('/programs/getPrograms');
  return res.data;
};
