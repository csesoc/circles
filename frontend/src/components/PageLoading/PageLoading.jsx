import React, { useEffect } from "react";
import { useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";
import circlesLogo from "assets/circlesWithBg.svg";
import S from "./styles";

const PageLoading = ({ setLoading }) => {
  const navigate = useNavigate();

  const degree = useSelector((state) => state.degree);

  const { pathname } = useLocation();
  // redirect index page to course selector
  const route = pathname === "/" ? "/course-selector" : pathname;

  useEffect(() => {
    setTimeout(() => {
      // check if this is a first time user
      navigate(!degree.isComplete ? "/degree-wizard" : route);
      setLoading(false);
    }, 750);
  }, []);

  return (
    <S.PageWrapper>
      <S.LoadingLogo src={circlesLogo} alt="Circles Logo" />
    </S.PageWrapper>
  );
};

export default PageLoading;
