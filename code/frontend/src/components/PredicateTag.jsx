// Notion's color palette for tags/labels
const NOTION_COLORS = [
  { name: 'gray', bg: 'rgba(235, 236, 237, 1)', text: 'rgba(55, 53, 47, 0.8)', border: 'rgba(55, 53, 47, 0.16)' },
  { name: 'brown', bg: 'rgba(238, 224, 218, 1)', text: 'rgba(141, 103, 71, 1)', border: 'rgba(141, 103, 71, 0.3)' },
  { name: 'orange', bg: 'rgba(250, 222, 201, 1)', text: 'rgba(217, 115, 13, 1)', border: 'rgba(217, 115, 13, 0.3)' },
  { name: 'yellow', bg: 'rgba(253, 236, 200, 1)', text: 'rgba(203, 145, 47, 1)', border: 'rgba(203, 145, 47, 0.3)' },
  { name: 'green', bg: 'rgba(219, 237, 219, 1)', text: 'rgba(68, 131, 97, 1)', border: 'rgba(68, 131, 97, 0.3)' },
  { name: 'blue', bg: 'rgba(211, 229, 239, 1)', text: 'rgba(30, 102, 140, 1)', border: 'rgba(30, 102, 140, 0.3)' },
  { name: 'purple', bg: 'rgba(232, 222, 238, 1)', text: 'rgba(133, 96, 136, 1)', border: 'rgba(133, 96, 136, 0.3)' },
  { name: 'pink', bg: 'rgba(245, 224, 233, 1)', text: 'rgba(193, 76, 138, 1)', border: 'rgba(193, 76, 138, 0.3)' },
  { name: 'red', bg: 'rgba(255, 226, 221, 1)', text: 'rgba(225, 97, 89, 1)', border: 'rgba(225, 97, 89, 0.3)' },
];

// Assign color to a tag based on its hash
const getTagColor = (tagName) => {
  if (!tagName) return NOTION_COLORS[0];
  // Simple hash function to consistently assign colors
  let hash = 0;
  for (let i = 0; i < tagName.length; i++) {
    hash = tagName.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % NOTION_COLORS.length;
  return NOTION_COLORS[index];
};

export default function PredicateTag({ predicate }) {
  const color = getTagColor(predicate);
  
  return (
    <span 
      className="predicate-tag"
      style={{
        backgroundColor: color.bg,
        color: color.text,
        borderColor: color.border,
      }}
    >
      {predicate}
    </span>
  );
}

