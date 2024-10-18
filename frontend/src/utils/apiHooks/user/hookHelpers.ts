import {
  useMutation,
  UseMutationOptions,
  UseMutationResult,
  useQuery,
  useQueryClient,
  UseQueryOptions
} from '@tanstack/react-query';
import useIdentity from 'hooks/useIdentity';

export type CreateUserQueryOptions = Omit<UseQueryOptions, 'queryKey' | 'queryFn' | 'enabled'>;
export type UserQueryHookOptions = {
  allowUnsetToken?: boolean;
  queryOptions?: Omit<UseQueryOptions, 'queryKey' | 'queryFn'>;
};

export function createUserQueryHook<
  const Key extends string[],
  const FArgs extends unknown[],
  const FRet
>(
  keySuffix: Key,
  fn: (token: string, ...args: FArgs) => Promise<FRet>,
  baseOptions?: CreateUserQueryOptions
) {
  return (options?: UserQueryHookOptions, ...args: FArgs) => {
    const { userId, token } = useIdentity(options?.allowUnsetToken === true) ?? {};

    const query = useQuery({
      queryKey: ['user', userId].concat(keySuffix),
      queryFn: () => fn(token!, ...args),

      // ...baseOptions,  // TODO-olli
      // ...options?.queryOptions,

      enabled: options?.queryOptions?.enabled && token !== undefined
    });

    return query;
  };
}

export type CreateUserMutationOptions<FArg, FRet> = Omit<
  UseMutationOptions<FRet, Error, FArg, unknown>,
  'mutationFn'
>;
export type UserMutationHookOptions<FArg, FRet> = {
  allowUnsetToken?: boolean;
  mutationOptions?: Omit<UseMutationOptions<FRet, Error, FArg, unknown>, 'mutationFn'>;
};

export function createUserMutationHook<
  const Keys extends true | string[][], // true signifies you want a full invalidate and clear
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
    const mutation = useMutation({
      mutationFn: async (data: FArg) =>
        token !== undefined ? fn(token, data) : Promise.reject(new Error('No token')),

      ...baseOptions,
      ...options?.mutationOptions,

      onSuccess: (data, variables, context) => {
        if (invalidationKeySuffixes === true) {
          queryClient.invalidateQueries({
            queryKey: ['user', userId]
          });

          queryClient.clear();
        } else {
          invalidationKeySuffixes.forEach((key) =>
            queryClient.invalidateQueries({
              queryKey: ['user', userId].concat(key)
            })
          );
        }

        if (options?.mutationOptions?.onSuccess !== undefined) {
          options.mutationOptions.onSuccess(data, variables, context);
        } else {
          baseOptions?.onSuccess?.(data, variables, context);
        }
      }
    });

    return mutation;
  };
}
