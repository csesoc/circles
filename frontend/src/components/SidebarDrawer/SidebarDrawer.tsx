import React, { useState } from 'react';
import S from './styles';

type Props = {
  children: React.ReactNode;
};

const SidebarDrawer = ({ children }: Props) => {
  const [open, setOpen] = useState<boolean | undefined>(undefined);

  return (
    <S.Wrapper $open={open} className="sidebar-drawer">
      <S.ButtonWrapper role="button" title="See Info..." onClick={() => setOpen(!open)}>
        <S.SVGWrapper xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 48">
          <S.SVGLine y1="2" y2="46" x1="2" x2="2" />
          <S.SVGLine y1="2" y2="46" x1="10" x2="10" />
        </S.SVGWrapper>
      </S.ButtonWrapper>
      <S.ChildrenWrapper>{children}</S.ChildrenWrapper>
    </S.Wrapper>
  );
};

export default SidebarDrawer;
