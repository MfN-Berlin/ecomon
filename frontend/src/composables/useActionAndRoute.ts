export const useActionAndRoute = ({ action, gotoUrl }: { action: () => void; gotoUrl: string }) => {
  const router = useRouter();
  return () => {
    try {
      console.log("actionAndRoute", action, gotoUrl);
      action();
      router.push(gotoUrl);
    } catch (error) {
      console.error(error);
    }
  };
};
