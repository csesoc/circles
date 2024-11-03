// eslint-disable-next-line no-console
export const errLogger = (loc: string) => (err: unknown) => console.error(`error at ${loc}: `, err);

export const unwrapQuery = <T>(data: T | undefined): T => {
  if (!data) {
    throw Error('tried to unwrap a query which was no settled');
  }
  return data;
};
