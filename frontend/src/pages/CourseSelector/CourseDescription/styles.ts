import styled from "styled-components";

const DescriptionWrapper = styled.div`
  padding: 1.6rem 2rem;
  display: flex;
  flex-direction: row;
  overflow: auto;
  font-size: 1rem;
`;

const DescriptionContent = styled.div`
  margin-right: 4rem;
  width: 75%;
`;

const AttributesContent = styled.div`
  width: 25%;
`;

const DescriptionTitleBar = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 10px;
`;

const AttributeWrapper = styled.div`
  border-bottom: #d9d9d9 solid 1px; // grey-5
  padding: 10px 0;
`;

const InfographicContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;

  & img {
    width: 70%;
    height: 70%;
    max-height: 500px;
  }
`;

export default {
  DescriptionWrapper,
  DescriptionContent,
  AttributesContent,
  DescriptionTitleBar,
  AttributeWrapper,
  InfographicContainer,
};
