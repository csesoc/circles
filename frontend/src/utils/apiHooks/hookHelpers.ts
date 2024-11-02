import {
  QueryClient,
  QueryKey,
  useMutation,
  UseMutationOptions,
  useQuery,
  useQueryClient,
  UseQueryOptions
} from '@tanstack/react-query';
import useIdentity from 'hooks/useIdentity';

// type KeyFnBase<FArgs extends unknown[]> = (...args: FArgs) => QueryKey;
type UserQueryKey<Key extends QueryKey> = ['user', uid: string, ...Key];

export type CreateUserQueryOptions<FRet, Key extends QueryKey> = Omit<
  UseQueryOptions<FRet, Error, FRet, UserQueryKey<Key>>,
  'queryKey' | 'queryFn' | 'enabled'
>;
export type UserQueryHookOptions<FRet, Key extends QueryKey> = {
  allowUnsetToken?: boolean;
  queryClient?: QueryClient;
  queryOptions?: Omit<
    UseQueryOptions<FRet, Error, FRet, UserQueryKey<Key>>,
    'queryKey' | 'queryFn'
  >;
};

export function createUserQueryHook<
  const Key extends QueryKey,
  const FArgs extends unknown[],
  const FRet
>(
  keySuffixFn: (...args: FArgs) => Key,
  fn: (token: string, ...args: FArgs) => Promise<FRet>,
  baseOptions?: CreateUserQueryOptions<FRet, Key>
) {
  return (options?: UserQueryHookOptions<FRet, Key>, ...args: FArgs) => {
    const { userId, token } = useIdentity(options?.allowUnsetToken === true) ?? {};

    const query = useQuery(
      {
        queryKey: ['user', userId!, ...keySuffixFn(...args)],
        queryFn: () => fn(token!, ...args),

        ...baseOptions,
        ...options?.queryOptions,

        enabled: options?.queryOptions?.enabled && token !== undefined
      },
      options?.queryClient
    );

    return query;
  };
}

export type CreateUserMutationOptions<FArg, FRet> = Omit<
  UseMutationOptions<FRet, Error, FArg, unknown>,
  'mutationFn'
>;

export type UserMutationHookOptions<FArg, FRet> = {
  allowUnsetToken?: boolean;
  queryClient?: QueryClient;
  mutationOptions?: Omit<UseMutationOptions<FRet, Error, FArg, unknown>, 'mutationFn'>;
};

export function createUserMutationHook<
  const Keys extends true | QueryKey[], // true signifies you want a full invalidate and clear
  const FRet,
  const FArg = void
>(
  invalidationKeySuffixes: Keys,
  fn: (token: string, data: FArg) => Promise<FRet>,
  baseOptions?: CreateUserMutationOptions<FArg, FRet>
) {
  return (options?: UserMutationHookOptions<FArg, FRet>) => {
    const { userId, token } = useIdentity(options?.allowUnsetToken === true) ?? {};

    const queryClient = useQueryClient();
    const mutation = useMutation(
      {
        mutationFn: async (data: FArg) =>
          token !== undefined ? fn(token, data) : Promise.reject(new Error('No token')),

        ...baseOptions,
        ...options?.mutationOptions,

        onSuccess: (data, variables, context) => {
          if (invalidationKeySuffixes === true) {
            queryClient.invalidateQueries({
              queryKey: ['user', userId]
            });

            // TODO-olli: figure out which one we want to do...
            // queryClient.resetQueries();
          } else {
            invalidationKeySuffixes.forEach((key) =>
              queryClient.invalidateQueries({
                queryKey: ['user', userId, ...key]
              })
            );
          }

          if (options?.mutationOptions?.onSuccess !== undefined) {
            options.mutationOptions.onSuccess(data, variables, context);
          } else {
            baseOptions?.onSuccess?.(data, variables, context);
          }
        }
      },
      options?.queryClient
    );

    return mutation;
  };
}

type StaticQueryKey<Key extends QueryKey> = ['static', ...Key];

export type CreateStaticQueryOptions<FRet, Key extends QueryKey> = Omit<
  UseQueryOptions<FRet, Error, FRet, StaticQueryKey<Key>>,
  'queryKey' | 'queryFn'
>;
export type StaticQueryHookOptions<FRet, Key extends QueryKey> = {
  allowUnsetToken?: boolean;
  queryClient?: QueryClient;
  queryOptions?: Omit<
    UseQueryOptions<FRet, Error, FRet, StaticQueryKey<Key>>,
    'queryKey' | 'queryFn'
  >;
};

export function createStaticQueryHook<
  const Key extends QueryKey,
  const FArgs extends unknown[],
  const FRet
>(
  keySuffixFn: (...args: FArgs) => Key,
  fn: (...args: FArgs) => Promise<FRet>,
  baseOptions?: CreateStaticQueryOptions<FRet, Key>
) {
  return (options?: StaticQueryHookOptions<FRet, Key>, ...args: FArgs) => {
    const query = useQuery(
      {
        queryKey: ['static', ...keySuffixFn(...args)],
        queryFn: () => fn(...args),

        ...baseOptions,
        ...options?.queryOptions
      },
      options?.queryClient
    );

    return query;
  };
}
