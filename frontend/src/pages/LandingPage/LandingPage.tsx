import React, { useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useUserSetupState } from 'utils/apiHooks/user';
import { importUser } from 'utils/export';
import PageLoading from 'components/PageLoading';
import { inDev } from 'config/constants';
import useToken from 'hooks/useToken';
import Footer from './FooterSection/Footer';
import GetInvolved from './GetInvolved';
import Hero from './Hero';
import HowToUse from './HowToUse';
import InteractiveViewSection from './InteractiveViewSection';
import KeyFeaturesSection from './KeyFeaturesSection';
import SponsorSection from './SponsorSection';

const LandingPage = () => {
  // THIS IS FOR MIGRATION. DELETE WHEN MIGRATION IS DONE
  const [searchParams, setSearchParams] = useSearchParams();
  const migration = searchParams.get('migration');
  if (migration) {
    try {
      const json = JSON.parse(migration) as JSON;
      // Throws error if migration is bad
      importUser(json);
      if (localStorage.getItem('oldUser') === null) {
        localStorage.setItem('oldUser', migration);
      } else {
        // eslint-disable-next-line no-console
        console.error('oldUser already exists');
      }
    } catch {
      // eslint-disable-next-line no-console
      console.error('Bad migration query param');
    }
    setSearchParams({});
    window.history.replaceState({}, document.title, window.location.pathname);
  }
  // END OF MIGRATION CODE

  // determine our next location
  const token = useToken({ allowUnset: true });

  const {
    data: userIsSetup,
    isPending,
    error
  } = useUserSetupState({
    allowUnsetToken: true,
    queryOptions: { refetchOnWindowFocus: 'always' }
  });

  const nextPage = useMemo(() => {
    if (token === undefined || userIsSetup === undefined || error) {
      // choose to throw them at login page if there is an error here, and expect it to retry/deal with it there
      // to avoid bad ux from reloading or error boundaries
      return '/login';
    }

    return userIsSetup ? '/course-selector' : '/degree-wizard';
  }, [token, userIsSetup, error]);

  if (error) {
    // eslint-disable-next-line no-console
    console.error(error);
  }

  if (isPending && token !== undefined) {
    return <PageLoading />;
  }

  return (
    <>
      <Hero startLocation={nextPage} />
      <SponsorSection />
      <KeyFeaturesSection />
      {inDev && <InteractiveViewSection />}
      <HowToUse />
      <GetInvolved />
      <Footer />
    </>
  );
};

export default LandingPage;
