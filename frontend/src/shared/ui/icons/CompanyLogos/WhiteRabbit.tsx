export const WhiteRabbitLogo: React.FC<{
  className?: string;
  width?: number;
  height?: number;
}> = ({ className = "", width = 16, height = 16 }) => {
  return (
    <div
      className={className}
      style={{
        width: width,
        height: height,
        backgroundImage: `url("/src/assets/whiteRabbit.png")`,
        backgroundRepeat: "no-repeat",
        backgroundSize: "100% auto",
        opacity: 0.5,
      }}
    ></div>
  );
};
