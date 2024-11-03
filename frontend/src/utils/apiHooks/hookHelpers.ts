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
  UseQueryOptions<FRet, Error, unknown, UserQueryKey<Key>>,
  'queryKey' | 'queryFn' | 'enabled' | 'select'
>;
export type UserQueryHookOptions<FRet, SelectFRet, Key extends QueryKey> = {
  allowUnsetToken?: boolean;
  queryClient?: QueryClient;
  queryOptions?: Omit<
    UseQueryOptions<FRet, Error, SelectFRet, UserQueryKey<Key>>,
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
  return <SelectFRet = FRet>(
    options?: UserQueryHookOptions<FRet, SelectFRet, Key>,
    ...args: FArgs
  ) => {
    const { userId, token } = useIdentity(options?.allowUnsetToken === true) ?? {};

    return useQuery<FRet, Error, SelectFRet, UserQueryKey<Key>>(
      {
        queryKey: ['user', userId!, ...keySuffixFn(...args)],
        queryFn: () => fn(token!, ...args),

        ...baseOptions,
        ...options?.queryOptions,

        enabled: options?.queryOptions?.enabled && token !== undefined
      },
      options?.queryClient
    );
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
  UseQueryOptions<FRet, Error, unknown, StaticQueryKey<Key>>,
  'queryKey' | 'queryFn' | 'enabled' | 'select'
>;
export type StaticQueryHookOptions<FRet, SelectFRet, Key extends QueryKey> = {
  queryClient?: QueryClient;
  queryOptions?: Omit<
    UseQueryOptions<FRet, Error, SelectFRet, StaticQueryKey<Key>>,
    'queryKey' | 'queryFn'
  >;
};

export function createStaticQueryHook<
  const Key extends QueryKey,
  const FArgs extends unknown[],
  const FRet
>(
  keySuffixFn: (...args: Parameters<typeof fn>) => Key,
  fn: (...args: FArgs) => Promise<FRet>,
  baseOptions?: CreateStaticQueryOptions<FRet, Key>
) {
  return <SelectFRet = FRet>(
    options?: StaticQueryHookOptions<FRet, SelectFRet, Key>,
    ...args: FArgs
  ) => {
    return useQuery<FRet, Error, SelectFRet, StaticQueryKey<Key>>(
      {
        queryKey: ['static', ...keySuffixFn(...args)],
        queryFn: () => fn(...args),

        ...baseOptions,
        ...options?.queryOptions
      },
      options?.queryClient
    );
  };
}
