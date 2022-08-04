import styled from "styled-components";

const Wrapper = styled.div`
  height: calc(100vh - var(--navbar-height));
  padding: 25px;
  display: flex;
  gap: 20px;
`;

const GraphPlaygroundWrapper = styled.div`
  height: 100%;
  border-radius: 20px;
  border: #C2C2C2 solid 1px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 5;
`;

const SidebarWrapper = styled.div`
  border-radius: 20px;
  border: #C2C2C2 solid 1px;
  padding: 10px;
  flex: 2;
`;

export default { Wrapper, GraphPlaygroundWrapper, SidebarWrapper };
